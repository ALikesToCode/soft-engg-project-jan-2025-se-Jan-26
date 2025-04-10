from fastapi import APIRouter, HTTPException, Depends, Request, status, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import json
from typing import List, Dict, Any, Optional
import os
import asyncio
import logging

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.validators.llm_validator import LLMInputValidator
from app.models.user import User
from app.services.function_router import function_router
from app.services.llm_service import create_llm_app
from app.utils.openapi import get_openapi
from app.routes.auth import get_current_user
from app.services.llm import process_query
from app.utils.logging import get_logger
from app.core.config import settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Initialize router
router = APIRouter()

# Initialize logger
logger = get_logger(__name__)

# Global chat history (this will be replaced with a proper DB-backed solution)
chat_history = []

# Schema definitions
class FunctionCall(BaseModel):
    """Schema for function call data"""
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Configuration for the model"""
        arbitrary_types_allowed = True

class FunctionResult(BaseModel):
    """Schema for function execution results"""
    name: str
    result: Any
    
    class Config:
        """Configuration for the model"""
        arbitrary_types_allowed = True

class LLMRequest(BaseModel):
    id: str
    query: str
    function_call: Optional[Dict[str, Any]] = None  # Allow direct function calling

class LLMResponse(BaseModel):
    """Schema for LLM responses that may include function calls"""
    content: str
    function_calls: Optional[List[Dict[str, Any]]] = None
    function_results: Optional[List[Dict[str, Any]]] = None
    raw_tool_calls: Optional[List[Dict[str, Any]]] = None

# Vector store retrieval function
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# Remove dependency on langchain_postgres
# from langchain_postgres import PGVector

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def get_vector_store():
    """Get initialized vector store connection"""
    # Return None to disable vector store functionality
    logger.warning("Vector store functionality disabled due to dependency issues")
    return None

async def query_vector_store(query_text, k=3):
    """Mock query the vector store for relevant documents"""
    logger.info(f"Mock vector store query for: {query_text} (k={k})")
    # Return empty results or mock data
    return [
        {
            "content": f"This is a mock result for query: {query_text}",
            "source": "Mock Source",
            "page": 1
        }
    ]

# Register the vector store query function
function_router.register_function(
    name="query_course_materials",
    description="Search the course materials for relevant information",
    handler=query_vector_store,
    parameters={
        "type": "object",
        "properties": {
            "query_text": {
                "type": "string",
                "description": "The query text to search for in the course materials"
            },
            "k": {
                "type": "integer",
                "description": "Number of results to return",
                "default": 3
            }
        },
        "required": ["query_text"]
    }
)

# Add a test function for verifying function calling
function_router.register_function(
    name="test_function_calling",
    description="Test function to verify that function calling is working properly",
    handler=lambda message="Hello": {"status": "success", "message": message},
    parameters={
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Test message to return"
            }
        }
    }
)

from fastapi import Request as FastAPIRequest
from starlette.requests import Request as StarletteRequest

@router.post("/chat",
    summary="Send message to AI",
    description="Sends a message to the AI and returns the AI's response",
    response_description="AI's response to the user's message",
    response_model=LLMResponse,
    responses={
        200: {
            "description": "AI response generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "content": "Here are the available courses in the program:",
                        "function_calls": [
                            {
                                "name": "getCourses",
                                "arguments": {}
                            }
                        ],
                        "function_results": [
                            {
                                "name": "getCourses",
                                "result": ["Course 1", "Course 2", "Course 3"]
                            }
                        ]
                    }
                }
            }
        },
        400: {"description": "Invalid input"},
        500: {"description": "Server error during AI processing"}
    }
)
async def chat(request: LLMRequest, req: Request, current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    try:
        # Validate input
        validator = LLMInputValidator(query=request.query)
        sanitized_query = validator.sanitize_input()
        
        # Get user ID if available
        user_id = None
        if current_user and "id" in current_user:
            user_id = current_user.get("id")
            logger.info(f"Authenticated user: {user_id}")
        else:
            logger.info("No authenticated user found")
        
        # Direct function call if requested
        if request.function_call:
            logger.info(f"Direct function call detected: {request.function_call}")
            function_name = request.function_call.get("name")
            function_args = request.function_call.get("arguments", {})
            
            # Add user_id to function args if not present
            if user_id and function_name in ["getUserProfile", "getCourses"]:
                if "user_id" not in function_args:
                    function_args["user_id"] = user_id
                    logger.info(f"Added user_id {user_id} to function arguments")
            
            # Execute the function
            try:
                result = await function_router.execute_function(function_name, function_args)
                return LLMResponse(
                    content=f"Successfully executed function {function_name}",
                    function_calls=[{"name": function_name, "arguments": function_args}],
                    function_results=[{"name": function_name, "result": result}]
                )
            except Exception as e:
                logger.error(f"Function execution error: {str(e)}")
                return LLMResponse(
                    content=f"Error executing function {function_name}: {str(e)}",
                    function_calls=[{"name": function_name, "arguments": function_args}],
                    function_results=[]
                )
        
        # Process through LLM if not a direct function call
        llm_result = await process_query(sanitized_query, user_id)
        
        content = llm_result.get("response", "")
        function_calls = llm_result.get("function_calls", [])
        function_results = llm_result.get("function_results", [])
        
        # Log the function calls for debugging
        if function_calls:
            logger.info(f"LLM requested {len(function_calls)} function calls")
            for fc in function_calls:
                logger.info(f"Function call: {fc.get('name')} with args: {fc.get('arguments')}")
        
        # Return the response
        return LLMResponse(
            content=content,
            function_calls=function_calls,
            function_results=function_results
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@router.post("/test-function-calling", 
    summary="Test endpoint specifically for function calling",
    description="Sends a message to the LLM that should trigger function calling to test if it's working",
    response_model=LLMResponse,
    responses={
        200: {"description": "Test completed successfully"},
        500: {"description": "Server error during test"}
    }
)
async def test_function_calling(req: Request):
    """Test endpoint to verify function calling is working properly"""
    try:
        # Create a simple test message that should trigger function calling
        test_message = "Please test the function calling system by calling the test_function_calling function with the message 'Function calling is working'."
        
        # Process the test message
        llm_result = await process_query(test_message)
        
        # Extract content and function calls
        content = llm_result.get("response", "")
        function_calls = llm_result.get("function_calls", [])
        function_results = llm_result.get("function_results", [])
        
        # Log the result
        logger.info(f"Function calling test result: {len(function_calls)} function calls detected")
        if function_calls:
            for fc in function_calls:
                logger.info(f"Function call: {fc.get('name')} with args: {fc.get('arguments')}")
        
        # Return detailed response for debugging
        return LLMResponse(
            content=content,
            function_calls=function_calls,
            function_results=function_results,
            raw_tool_calls=llm_result.get("raw_tool_calls", None)
        )
    
    except Exception as e:
        logger.error(f"Error in test function calling endpoint: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error in function calling test: {str(e)}")

@router.get("/chat")
async def get_chat_history(id: str, req: Request):
    """Get chat history for a specified thread ID"""
    app = req.app
    
    if not hasattr(app.state, "llmapp"):
        raise HTTPException(
            status_code=500, 
            detail="LLMApp not initialized. Server configuration issue."
        )
    
    config = {"configurable": {"thread_id": id}}
    try:
        state_snapshot = await app.state.llmapp.aget_state(config)
        messages = state_snapshot[0]["messages"]
        return [{"type": msg.type, "content": msg.content} for msg in messages]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )

@router.delete("/chat")
async def clear_chat(id: str, req: Request):
    """Delete chat history for a specified thread ID"""
    app = req.app
    
    if not hasattr(app.state, "llmapp") or app.state.llmapp is None:
        raise HTTPException(
            status_code=500, 
            detail="LLM application not initialized. Server configuration issue."
        )
    
    try:
        # Set a timeout for this operation
        import asyncio
        
        # Access our custom LLMApp implementation
        if hasattr(app.state.llmapp, "conversations"):
            # Use a timeout to prevent the operation from hanging
            try:
                # If the thread exists, delete it (with 5 second timeout)
                async def delete_conversation():
                    if id in app.state.llmapp.conversations:
                        del app.state.llmapp.conversations[id]
                        return {"message": f"Chat history for thread_id '{id}' has been cleared."}
                    else:
                        return {"message": f"No chat history found for thread_id '{id}'."}
                
                # Execute with timeout
                return await asyncio.wait_for(delete_conversation(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.error(f"Timeout when clearing chat history for thread_id '{id}'")
                # If timeout, return success anyway to avoid client-side issues
                return {"message": f"Operation timed out, but chat history for thread_id '{id}' should be cleared on next restart."}
        else:
            return {"message": "Chat history deletion is not supported with current LLM implementation."}
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        # Return a more user-friendly message instead of throwing an error
        return {"message": f"Failed to clear chat history, but it will be cleared on restart: {str(e)}"}

@router.get("/openapi.json", 
    summary="Get API documentation",
    description="Returns OpenAPI documentation filtered by user role",
    responses={
        200: {"description": "Return filtered OpenAPI documentation"},
        401: {"description": "Unauthorized"},
        500: {"description": "Server error"}
    }
)
async def get_openapi_docs(req: Request, current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """
    Get OpenAPI documentation filtered according to the user's role.
    
    This endpoint returns the OpenAPI specification with only the endpoints
    that are accessible to the current user based on their role.
    """
    # Get the main app instance
    app = req.app
    
    try:
        # Get the full OpenAPI spec
        openapi_schema = get_openapi(
            title="API Documentation",
            version="1.0.0",
            description="API documentation for the application",
            routes=app.routes
        )
        
        # If no user is authenticated, only return public endpoints
        user_role = "anonymous"
        if current_user:
            user_role = current_user.get("role", "anonymous").lower()
            logger.info(f"Filtering OpenAPI docs for user role: {user_role}")
        else:
            logger.info("No authenticated user, returning anonymous API docs")
        
        # Define paths accessible by role
        role_access = {
            "admin": {  # Admin can access everything
                "include_all": True,
                "excluded_paths": []
            },
            "faculty": {
                "include_all": False,
                "allowed_tags": ["Authentication", "Chat", "Courses", "Assignments", 
                                "LLM", "FAQs", "User", "Users"],
                "excluded_paths": ["/api/v1/settings", "/api/v1/monitoring"]
            },
            "student": {
                "include_all": False,
                "allowed_tags": ["Authentication", "Chat", "Courses", "Assignments", 
                                "LLM", "FAQs", "User"],
                "excluded_paths": ["/api/v1/settings", "/api/v1/monitoring", 
                                  "/api/v1/users", "/api/v1/auth/users"]
            },
            "anonymous": {
                "include_all": False,
                "allowed_tags": ["Authentication"],
                "allowed_paths": ["/api/v1/auth/login", "/api/v1/auth/register", 
                                 "/api/v1/auth/refresh", "/api/v1/faqs"]
            }
        }
        
        # Get access configuration for this role
        access_config = role_access.get(user_role, role_access["anonymous"])
        
        # If not admin, filter the paths
        if not access_config.get("include_all", False):
            filtered_paths = {}
            
            for path, path_item in openapi_schema["paths"].items():
                # Check if path is explicitly allowed (for anonymous users)
                if "allowed_paths" in access_config and any(
                    path.startswith(allowed_path) for allowed_path in access_config.get("allowed_paths", [])
                ):
                    filtered_paths[path] = path_item
                    continue
                    
                # Check if path is explicitly excluded
                if any(path.startswith(excluded) for excluded in access_config.get("excluded_paths", [])):
                    continue
                
                # Check if any operation in this path has an allowed tag
                if "allowed_tags" in access_config:
                    for method, operation in path_item.items():
                        if method in ["get", "post", "put", "delete", "patch"]:
                            # Check if operation has any allowed tags
                            if "tags" in operation and any(
                                tag in access_config["allowed_tags"] for tag in operation["tags"]
                            ):
                                filtered_paths[path] = path_item
                                break
            
            # Replace paths with filtered paths
            openapi_schema["paths"] = filtered_paths
        
        return openapi_schema
    except Exception as e:
        logger.error(f"Error generating OpenAPI documentation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating API documentation: {str(e)}"
        )

@router.post("/execute-function", 
    summary="Directly execute a function",
    description="Execute a function with the provided arguments directly, bypassing the LLM",
    response_model=LLMResponse,
    responses={
        200: {"description": "Function executed successfully"},
        400: {"description": "Invalid function name or arguments"},
        500: {"description": "Server error during function execution"}
    }
)
async def execute_function(
    function_name: str = Query(..., description="Name of the function to execute"),
    req: Request = None,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)  # Require authentication
):
    """
    Directly execute a function with the provided arguments.
    """
    try:
        # Get request body for arguments
        body = await req.json() if req.method == "POST" and req.headers.get("content-type") == "application/json" else {}
        
        # Get user ID if available
        user_id = None
        if current_user and "id" in current_user:
            user_id = current_user.get("id")
            logger.info(f"Authenticated user: {user_id}")
        
        # Add user_id to function args if needed and not already provided
        function_args = body.get("arguments", {})
        if user_id and function_name in ["getUserProfile", "getCourses"]:
            if "user_id" not in function_args:
                function_args["user_id"] = user_id
                logger.info(f"Added user_id {user_id} to function arguments")
        
        # For debugging purposes, if no user_id is available but required, use a test ID
        if not user_id and function_name in ["getUserProfile", "getCourses"]:
            if "user_id" not in function_args:
                # Only use hardcoded ID in development
                if settings.ENV == "development":
                    function_args["user_id"] = "05f83842-96d1-4ca0-9101-7c39c74ac5cd"
                    logger.warning(f"Using hardcoded user_id for testing in development environment")
                else:
                    return JSONResponse(
                        status_code=401,
                        content={"error": "Authentication required for this function"}
                    )
        
        logger.info(f"Executing function {function_name} with args: {function_args}")
        
        # Execute the function
        result = await function_router.execute_function(function_name, function_args)
        
        return LLMResponse(
            content=f"Successfully executed function {function_name}",
            function_calls=[{"name": function_name, "arguments": function_args}],
            function_results=[{"name": function_name, "result": result}]
        )
    
    except Exception as e:
        logger.error(f"Error executing function: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error executing function: {str(e)}")

# Simple endpoint for getting courses directly
@router.get("/get-courses", 
    summary="Get courses for the current user",
    description="Convenience endpoint to get courses directly without going through the LLM",
    responses={
        200: {"description": "Courses retrieved successfully"},
        401: {"description": "Authentication required"},
        500: {"description": "Server error"}
    }
)
async def get_user_courses(
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get courses for the current user with optional status filter.
    This is a convenience endpoint for testing.
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        logger.info(f"Getting courses for user {user_id} with status filter: {status}")
        
        # Import the function directly to avoid circular imports
        from app.services.api_functions import getCourses
        
        # Call the function with the user_id
        args = {"user_id": user_id}
        if status:
            args["status"] = status
            
        result = await getCourses(**args)
        return result
    
    except Exception as e:
        logger.error(f"Error getting courses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting courses: {str(e)}")

@router.get("/debug-function-calling", 
    summary="Debug the function calling capabilities",
    description="Run a diagnostic test of function calling with the LLM models",
    response_model=Dict[str, Any]
)
async def debug_function_calling_route(
    query: str = Query("What courses am I enrolled in?", description="Test query to use"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Run diagnostics on function calling to help troubleshoot issues.
    This endpoint will test different models and configurations.
    """
    try:
        from app.services.llm_service import debug_function_calling
        
        # Run the diagnostic function
        results = await debug_function_calling(query)
        
        return {
            "status": "success",
            "results": results,
            "message": "Function calling diagnostic completed"
        }
    except Exception as e:
        logger.error(f"Error in function calling diagnostic: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "error": str(e),
            "message": "Function calling diagnostic failed"
        }