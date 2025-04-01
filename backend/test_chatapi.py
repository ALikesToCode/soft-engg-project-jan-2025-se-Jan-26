"""
Simple script to test the available-functions endpoint.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
import uvicorn

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002) 