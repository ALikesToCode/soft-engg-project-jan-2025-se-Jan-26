"""
Simple script to test the available-functions endpoint.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
import uvicorn
import requests
import json
import os

# Define a dummy dependency to replace get_current_user
async def dummy_current_user():
    """Dummy get_current_user function that always returns a student user"""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "role": "student"
    }

# Create a FastAPI app
app = FastAPI()

@app.get("/api/v1/chat/available-functions", response_model=List[Dict[str, Any]])
async def get_available_functions(current_user: Optional[Dict[str, Any]] = Depends(dummy_current_user)):
    """Get available functions for the AI to call"""
    return [
        {
            "name": "web_search",
            "description": "Search the web for current information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "getCourses",
            "description": "Get all available courses for the current user",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "getCourseById",
            "description": "Get details of a specific course by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "courseId": {
                        "type": "string",
                        "description": "The ID of the course to retrieve"
                    }
                },
                "required": ["courseId"]
            }
        }
    ]

def get_token():
    """Get a token for testing the API"""
    # Try to read from token.txt file
    try:
        if os.path.exists("token.txt"):
            with open("token.txt", "r") as f:
                token = f.read().strip()
                if token:
                    return token
    except Exception as e:
        print(f"Error reading token file: {e}")
    
    # If no token file, try to login
    try:
        login_payload = {
            "username": "admin@example.com",  # Replace with your test credentials
            "password": "adminpassword"      # Replace with your test credentials
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login", 
            json=login_payload
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            # Save token for future use
            with open("token.txt", "w") as f:
                f.write(token)
            return token
    except Exception as e:
        print(f"Error logging in: {e}")
    
    print("Unable to get authentication token. Please provide one manually.")
    return None

def test_debug_endpoint():
    """Test the debug endpoint with a proper payload"""
    base_url = "http://localhost:8000"  # Adjust if needed
    
    # Create a valid payload with the required query field
    payload = {
        "id": "test-123",
        "query": "Hello, how can you help me?"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Get token for authorization
    token = get_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Print test setup
    print(f"\nTesting debug endpoint with payload: {json.dumps(payload, indent=2)}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    
    try:
        # Test the debug endpoint
        debug_url = f"{base_url}/api/v1/llm/chat/debug"
        print(f"Making POST request to: {debug_url}")
        
        debug_response = requests.post(
            debug_url,
            json=payload,
            headers=headers
        )
        
        print("\nDebug endpoint response:")
        print(f"Status code: {debug_response.status_code}")
        
        # Try to parse JSON response
        try:
            response_data = debug_response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            if debug_response.status_code == 200:
                print("Debug test successful!")
                return True
        except Exception as e:
            print(f"Error parsing debug response: {e}")
            print(f"Raw response: {debug_response.text}")
        
        return False
    except Exception as e:
        print(f"Debug test error: {str(e)}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint with a proper payload"""
    base_url = "http://localhost:8000"  # Adjust if needed
    
    # Create a valid payload with the required query field
    payload = {
        "id": "test-123",
        "query": "Hello, how can you help me?"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Get token for authorization
    token = get_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        print("No token available, test will likely fail")
    
    # Print test setup with more detailed information
    print(f"\nTesting chat endpoint with payload: {json.dumps(payload, indent=2)}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Request URL: {base_url}/api/v1/llm/chat")
    
    # Debug: Show the exact format being sent to verify all required fields
    try:
        # Convert to the exact format being sent over the wire
        request_body = json.dumps(payload)
        print(f"Request body string: {request_body}")
    except Exception as e:
        print(f"Error serializing payload: {e}")
    
    try:
        # Test the chat endpoint
        chat_url = f"{base_url}/api/v1/llm/chat"
        print(f"Making POST request to: {chat_url}")
        
        chat_response = requests.post(
            chat_url,
            json=payload,  # This is automatically converted to JSON
            headers=headers
        )
        
        print("\nChat endpoint response:")
        print(f"Status code: {chat_response.status_code}")
        
        # Try to parse JSON response
        try:
            response_data = chat_response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Raw response: {chat_response.text}")
        
        return chat_response.status_code == 200
    except Exception as e:
        print(f"Test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Running chat API tests...")
    
    # Option 1: Run the FastAPI app
    # uvicorn.run(app, host="0.0.0.0", port=8002)
    
    # Option 2: Test the endpoints
    debug_success = test_debug_endpoint()
    print(f"Debug test {'passed' if debug_success else 'failed'}")
    
    chat_success = test_chat_endpoint()
    print(f"Chat test {'passed' if chat_success else 'failed'}") 