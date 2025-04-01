import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.models.user import User
from app.utils.jwt_utils import create_access_token
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
async def faculty_token(test_users):
    """Create a valid faculty token for testing"""
    # Ensure test_users is awaited if it's a coroutine
    users = await test_users if isinstance(test_users, object) and hasattr(test_users, "__await__") else test_users
    
    return create_access_token({
        "email": "faculty@test.com",
        "role": "faculty",
        "sub": str(users["faculty"].id)
    })

@pytest.fixture
async def student_token(test_users):
    """Create a valid student token for testing"""
    # Ensure test_users is awaited if it's a coroutine
    users = await test_users if isinstance(test_users, object) and hasattr(test_users, "__await__") else test_users
    
    return create_access_token({
        "email": "student@test.com",
        "role": "student",
        "sub": str(users["student"].id)
    })

# Mock LLM response for testing
class MockLLMResponse:
    def __init__(self, content, additional_kwargs=None):
        self.content = content
        self.additional_kwargs = additional_kwargs or {}

# Chat endpoint tests
@pytest.mark.asyncio
@patch('app.routes.llm.get_chat_history')
async def test_get_chat_history(mock_history, client, student_token):
    """Test getting chat history"""
    # Mock the chat history response
    mock_history.return_value = [
        {"role": "system", "content": "I am an AI assistant."},
        {"role": "user", "content": "Hello, how can you help me?"},
        {"role": "assistant", "content": "I can help you with your questions about courses and assignments."}
    ]
    
    # Send request
    response = client.get(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["role"] == "system"
    assert data[1]["role"] == "user"
    assert data[2]["role"] == "assistant"

@pytest.mark.asyncio
@patch('app.routes.llm.llm')
async def test_chat_basic_response(mock_llm, client, student_token):
    """Test basic chat functionality without function calls"""
    # Mock LLM response
    mock_llm.invoke.return_value = MockLLMResponse(content="This is a test response")
    
    # Send chat request
    response = client.post(
        "/api/chat",
        json={"message": "Hello, how are you?"},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert data["message"] == "This is a test response"
    assert "function_call" not in data

@pytest.mark.asyncio
@patch('app.routes.llm.llm')
@patch('app.routes.llm.function_router.execute_function')
async def test_chat_with_function_call(mock_execute_function, mock_llm, client, student_token):
    """Test chat with function calling capability"""
    # Mock function execution
    mock_execute_function.return_value = {"result": "Function result"}
    
    # Mock LLM responses - first with function call, then with final response
    function_call = {
        "name": "web_search",
        "arguments": json.dumps({"query": "test query"})
    }
    
    mock_llm.invoke.side_effect = [
        # First response with function call
        MockLLMResponse(
            content="I'll search for that information",
            additional_kwargs={"function_call": function_call}
        ),
        # Second response after function execution
        MockLLMResponse(content="Here's what I found: Function result")
    ]
    
    # Send chat request
    response = client.post(
        "/api/chat",
        json={"message": "Search for test query"},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Here's what I found: Function result"
    assert "function_call" in data
    assert data["function_call"]["name"] == "web_search"

@pytest.mark.asyncio
@patch('app.routes.llm.llm')
@patch('app.routes.llm.function_router.execute_function')
async def test_chat_with_function_error(mock_execute_function, mock_llm, client, student_token):
    """Test chat with function execution error"""
    # Mock function execution to raise an error
    mock_execute_function.side_effect = Exception("Function execution failed")
    
    # Mock LLM responses
    function_call = {
        "name": "web_search",
        "arguments": json.dumps({"query": "test query"})
    }
    
    mock_llm.invoke.side_effect = [
        # First response with function call
        MockLLMResponse(
            content="I'll search for that information",
            additional_kwargs={"function_call": function_call}
        ),
        # Second response after function error
        MockLLMResponse(content="I encountered an error while searching")
    ]
    
    # Send chat request
    response = client.post(
        "/api/chat",
        json={"message": "Search for test query"},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "error" in data
    assert "Function execution failed" in data["error"]

@pytest.mark.asyncio
async def test_chat_with_invalid_input(client, student_token):
    """Test chat with invalid input"""
    # Empty query
    chat_data = {
        "query": "",
        "max_tokens": 1024
    }
    
    # Send chat request
    response = client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {student_token}"},
        json=chat_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_chat_with_sql_injection(client, student_token):
    """Test chat with SQL injection attempt"""
    # SQL injection attempt
    chat_data = {
        "query": "SELECT * FROM users",
        "max_tokens": 1024
    }
    
    # Send chat request
    response = client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {student_token}"},
        json=chat_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
@patch('app.routes.llm.function_router.get_function_declarations')
async def test_get_available_functions(mock_get_functions, client, student_token):
    """Test getting available functions"""
    # Mock the function declarations
    mock_get_functions.return_value = [
        {
            "name": "get_courses",
            "description": "Get a list of available courses",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Course category"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of courses to return"
                    }
                }
            }
        },
        {
            "name": "web_search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        }
    ]
    
    # Send request
    response = client.get(
        "/api/v1/available-functions",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "get_courses"
    assert data[1]["name"] == "web_search"

@pytest.mark.asyncio
@patch('app.routes.llm.function_router.execute_function')
async def test_execute_function(mock_execute, client, student_token):
    """Test executing a function directly"""
    # Mock function execution
    mock_execute.return_value = {
        "courses": [
            {
                "id": "course_1",
                "name": "Introduction to Computer Science",
                "code": "CS101"
            }
        ]
    }
    
    # Function request data
    function_data = {
        "query": "get_courses",
        "max_tokens": 1024
    }
    
    # Send request
    response = client.post(
        "/api/v1/execute-function",
        headers={"Authorization": f"Bearer {student_token}"},
        json=function_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "result" in data
    assert "courses" in data["result"]
    assert len(data["result"]["courses"]) == 1
    assert data["result"]["courses"][0]["name"] == "Introduction to Computer Science"

@pytest.mark.asyncio
@patch('app.routes.llm.web_search')
async def test_web_search_function(mock_web_search, client, student_token):
    """Test the web search function"""
    # Mock web search results
    mock_web_search.return_value = [
        {
            "title": "Introduction to Computer Science",
            "snippet": "Computer Science is the study of computers and computational systems...",
            "url": "https://example.com/cs-intro"
        },
        {
            "title": "Computer Science Curriculum",
            "snippet": "A comprehensive curriculum for learning computer science...",
            "url": "https://example.com/cs-curriculum"
        }
    ]
    
    # Function request data
    function_data = {
        "query": "web_search",
        "max_tokens": 1024,
        "search_query": "computer science introduction"
    }
    
    # Send request
    response = client.post(
        "/api/v1/execute-function",
        headers={"Authorization": f"Bearer {student_token}"},
        json=function_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "result" in data
    assert isinstance(data["result"], list)
    assert len(data["result"]) == 2
    assert data["result"][0]["title"] == "Introduction to Computer Science"
    assert "url" in data["result"][0]
    assert "snippet" in data["result"][0] 