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
    # This test is just a placeholder to ensure the function exists and returns True
    # The actual functionality is tested in other tests
    result = await startNewChat()
    assert result is True

@pytest.mark.asyncio
@patch('app.routes.llm.llm')
async def test_chat_basic_response(mock_llm, client, reset_chat_history):
    """Test basic chat functionality without function calls"""
    # Mock LLM response
    mock_llm.invoke.return_value = MockLLMResponse(content="This is a test response")
    
    # Send chat request
    response = client.post(
        "/chat",
        json={"query": "Hello, how are you?", "max_tokens": 1024}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "response" in data
    assert data["response"] == "This is a test response"
    assert "function_call" not in data

@pytest.mark.asyncio
@patch('app.routes.llm.llm')
@patch('app.services.function_router.function_router.execute_function')
async def test_chat_with_function_call(mock_execute_function, mock_llm, client, reset_chat_history):
    """Test chat with function call"""
    # Mock function call in LLM response
    function_call = {
        "name": "test_function",
        "arguments": json.dumps({"param1": "test", "param2": 123})
    }
    mock_llm.invoke.return_value = MockLLMResponse(
        content="I'll help you with that",
        additional_kwargs={"function_call": function_call}
    )
    
    # Mock function execution result
    mock_execute_function.return_value = {"result": "Function executed successfully"}
    
    # Send chat request
    response = client.post(
        "/chat",
        json={"query": "Call a function", "max_tokens": 1024}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "response" in data
    assert "function_call" in data
    assert data["function_call"]["name"] == "test_function"
    assert "function_response" in data
    assert data["function_response"]["result"] == "Function executed successfully"

@pytest.mark.asyncio
@patch('app.routes.llm.llm')
async def test_chat_with_invalid_input(mock_llm, client):
    """Test chat with invalid input"""
    response = client.post(
        "/chat",
        json={"query": "", "max_tokens": 1024}  # Empty query
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
@patch('app.routes.llm.llm')
async def test_chat_with_sql_injection(mock_llm, client):
    """Test chat with SQL injection attempt"""
    # Mock LLM response
    mock_llm.invoke.return_value = MockLLMResponse(content="This is a safe response")
    
    # Send chat request with SQL injection attempt
    response = client.post(
        "/chat",
        json={"query": "SELECT * FROM users; DROP TABLE users;", "max_tokens": 1024}
    )
    
    # Check that the request is processed normally (validation happens at LLM level)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
@patch('app.routes.llm.llm')
@patch('app.services.function_router.function_router.execute_function')
async def test_chat_with_function_error(mock_execute_function, mock_llm, client, reset_chat_history):
    """Test chat with function execution error"""
    # Mock function call in LLM response
    function_call = {
        "name": "test_function",
        "arguments": json.dumps({"param1": "test", "param2": 123})
    }
    mock_llm.invoke.return_value = MockLLMResponse(
        content="I'll help you with that",
        additional_kwargs={"function_call": function_call}
    )
    
    # Mock function execution error
    mock_execute_function.side_effect = Exception("Function execution failed")
    
    # Send chat request
    response = client.post(
        "/chat",
        json={"query": "Call a function", "max_tokens": 1024}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "response" in data
    assert "function_call" in data
    assert "function_error" in data
    assert "Function execution failed" in data["function_error"]

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
