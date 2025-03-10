import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.routes.llm import router, startNewChat, chat_history
from app.validators.llm_validator import LLMInputValidator
from app.services.function_router import function_router, FunctionRouter
from main import app

# Test fixtures
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client():
    async with AsyncClient(base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def reset_chat_history():
    """Reset chat history before each test"""
    global chat_history
    chat_history = []
    return True

# Mock LLM response for testing
class MockLLMResponse:
    def __init__(self, content, additional_kwargs=None):
        self.content = content
        self.additional_kwargs = additional_kwargs or {}

# Tests for chat endpoint
@pytest.mark.asyncio
async def test_start_new_chat():
    """Test starting a new chat session"""
    # Clear existing chat history
    global chat_history
    chat_history = [HumanMessage(content="Previous message")]
    
    # Start new chat
    result = await startNewChat()
    
    # Verify result and chat history
    assert result is True
    assert len(chat_history) == 1
    assert isinstance(chat_history[0], SystemMessage)

@pytest.mark.asyncio
@patch('app.routes.llm.llm.ainvoke')
async def test_chat_basic_response(mock_ainvoke, client, reset_chat_history):
    """Test basic chat functionality without function calls"""
    # Mock LLM response
    mock_ainvoke.return_value = MockLLMResponse(content="This is a test response")
    
    # Send chat request
    response = client.post(
        "/chat",
        json={"query": "Hello, how are you?", "max_tokens": 1024}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["content"] == "This is a test response"
    assert "function_calls" not in data or data["function_calls"] is None
    
    # Verify LLM was called with correct parameters
    mock_ainvoke.assert_called_once()
    args, kwargs = mock_ainvoke.call_args
    assert len(args[0]) == 2  # System message + user message
    assert isinstance(args[0][0], SystemMessage)
    assert isinstance(args[0][1], HumanMessage)
    assert args[0][1].content == "Hello, how are you?"

@pytest.mark.asyncio
@patch('app.routes.llm.llm.ainvoke')
@patch('app.services.function_router.function_router.execute_function')
async def test_chat_with_function_call(mock_execute_function, mock_ainvoke, client, reset_chat_history):
    """Test chat with function calling capability"""
    # Mock function execution
    mock_execute_function.return_value = {"result": "Function result"}
    
    # Mock LLM responses - first with function call, then with final response
    mock_ainvoke.side_effect = [
        # First response with function call
        MockLLMResponse(
            content="I'll search for that information",
            additional_kwargs={
                "tool_calls": [
                    {
                        "function": {
                            "name": "web_search",
                            "arguments": json.dumps({"query": "test query"})
                        }
                    }
                ]
            }
        ),
        # Second response after function execution
        MockLLMResponse(content="Here's what I found: Function result")
    ]
    
    # Send chat request
    response = client.post(
        "/chat",
        json={"query": "Search for test query"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["content"] == "Here's what I found: Function result"
    assert data["function_calls"] is not None
    assert len(data["function_calls"]) == 1
    assert data["function_calls"][0]["name"] == "web_search"
    
    # Verify function was executed
    mock_execute_function.assert_called_once_with("web_search", {"query": "test query"})
    
    # Verify LLM was called twice (initial + after function call)
    assert mock_ainvoke.call_count == 2

@pytest.mark.asyncio
@patch('app.routes.llm.llm.ainvoke')
async def test_chat_with_invalid_input(mock_ainvoke, client):
    """Test chat with invalid input"""
    # Send empty query
    response = client.post(
        "/chat",
        json={"query": ""}
    )
    
    # Check response
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Verify LLM was not called
    mock_ainvoke.assert_not_called()

@pytest.mark.asyncio
@patch('app.routes.llm.llm.ainvoke')
async def test_chat_with_sql_injection(mock_ainvoke, client):
    """Test chat with SQL injection attempt"""
    # Send SQL injection attempt
    response = client.post(
        "/chat",
        json={"query": "SELECT * FROM users"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Verify LLM was not called
    mock_ainvoke.assert_not_called()

@pytest.mark.asyncio
@patch('app.routes.llm.llm.ainvoke')
@patch('app.services.function_router.function_router.execute_function')
async def test_chat_with_function_error(mock_execute_function, mock_ainvoke, client, reset_chat_history):
    """Test chat with function execution error"""
    # Mock function execution to raise an error
    mock_execute_function.side_effect = Exception("Function execution failed")
    
    # Mock LLM responses
    mock_ainvoke.side_effect = [
        # First response with function call
        MockLLMResponse(
            content="I'll search for that information",
            additional_kwargs={
                "tool_calls": [
                    {
                        "function": {
                            "name": "web_search",
                            "arguments": json.dumps({"query": "test query"})
                        }
                    }
                ]
            }
        ),
        # Second response after function error
        MockLLMResponse(content="I encountered an error while searching")
    ]
    
    # Send chat request
    response = client.post(
        "/chat",
        json={"query": "Search for test query"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["content"] == "I encountered an error while searching"
    
    # Verify function was attempted
    mock_execute_function.assert_called_once()
    
    # Verify error was handled and LLM was called again
    assert mock_ainvoke.call_count == 2

# Tests for function router
def test_function_router_registration():
    """Test function registration in the router"""
    # Create a test router
    test_router = FunctionRouter()
    
    # Register a test function
    async def test_function(param1: str, param2: int):
        return {"result": f"{param1} {param2}"}
    
    test_router.register_function(
        name="test_function",
        description="A test function",
        handler=test_function,
        parameters={
            "type": "object",
            "properties": {
                "param1": {"type": "string"},
                "param2": {"type": "integer"}
            }
        }
    )
    
    # Verify function was registered
    declarations = test_router.get_function_declarations()
    assert len(declarations) == 1
    assert declarations[0]["name"] == "test_function"
    assert declarations[0]["description"] == "A test function"

@pytest.mark.asyncio
async def test_function_router_execution():
    """Test function execution through the router"""
    # Create a test router
    test_router = FunctionRouter()
    
    # Register a test function
    async def test_function(param1: str, param2: int):
        return {"result": f"{param1} {param2}"}
    
    test_router.register_function(
        name="test_function",
        description="A test function",
        handler=test_function,
        parameters={
            "type": "object",
            "properties": {
                "param1": {"type": "string"},
                "param2": {"type": "integer"}
            }
        }
    )
    
    # Execute the function
    result = await test_router.execute_function(
        "test_function", 
        {"param1": "hello", "param2": 42}
    )
    
    # Verify result
    assert result == {"result": "hello 42"}

@pytest.mark.asyncio
async def test_function_router_execution_error():
    """Test error handling in function execution"""
    # Create a test router
    test_router = FunctionRouter()
    
    # Register a test function that raises an error
    async def error_function():
        raise ValueError("Test error")
    
    test_router.register_function(
        name="error_function",
        description="A function that raises an error",
        handler=error_function,
        parameters={"type": "object", "properties": {}}
    )
    
    # Execute the function and expect an exception
    with pytest.raises(Exception):
        await test_router.execute_function("error_function", {})

@pytest.mark.asyncio
async def test_web_search_function():
    """Test the web_search function"""
    # Call the web search function
    results = await function_router.web_search("test query")
    
    # Verify results
    assert isinstance(results, list)
    assert len(results) > 0
    for result in results:
        assert "title" in result
        assert "snippet" in result
        assert "url" in result
