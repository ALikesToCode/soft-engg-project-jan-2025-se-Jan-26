from fastapi import APIRouter, HTTPException, Depends, Request, status
from pydantic import BaseModel, Field
import json
from typing import List, Dict, Any, Optional
import os

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
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Schema definitions
class FunctionCall(BaseModel):
    """Schema for function call data"""
    name: str
    arguments: Dict[str, Any]

class FunctionResult(BaseModel):
    """Schema for function execution results"""
    name: str
    result: Any

class LLMRequest(BaseModel):
    id: str
    query: str

class LLMResponse(BaseModel):
    """Schema for LLM responses that may include function calls"""
    content: str
    function_calls: Optional[List[FunctionCall]] = None
    function_results: Optional[List[FunctionResult]] = None
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
    """
    Send a message to the AI and get a response with potential function calls.
    
    This endpoint processes the user's message using the Gemini AI model,
    allowing it to call functions when needed to gather information.
    
    Args:
        request: The validated LLM request containing the user's message
        
    Returns:
        LLMResponse containing the AI's response and any function calls made
        
    Raises:
        HTTPException: If input validation fails or if there's an error generating the response
    """
    try:
        # Use the app state to get the LLMApp
        app = req.app
        
        if not hasattr(app.state, "llmapp") or not app.state.llmapp:
            # Handle initial startup - retry with exponential backoff
            max_init_retries = 3
            for retry in range(max_init_retries):
                logger.warning(f"LLMApp not initialized. Attempting to initialize (attempt {retry+1}/{max_init_retries})")
                try:
                    # Try to initialize LLMApp if possible
                    from app.services.llm_service import create_llm_app
                    await create_llm_app(app)
                    logger.info("LLMApp initialization successful")
                    break
                except Exception as init_error:
                    logger.error(f"LLMApp initialization error: {str(init_error)}")
                    import asyncio
                    await asyncio.sleep(1 * (2 ** retry))  # Exponential backoff
            
            # If still not initialized, return fallback response
            if not hasattr(app.state, "llmapp") or not app.state.llmapp:
                logger.error("LLMApp initialization failed, returning fallback response")
                return LLMResponse(
                    content="I'm sorry, I'm still starting up. Please try again in a moment."
                )
            
        config = {"configurable": {"thread_id": request.id}}
        input_message = [HumanMessage(content=request.query)]
        
        # Get available functions
        tools = function_router.get_function_declarations()
        
        # Attempt to invoke the LLMApp with retry logic
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Invoke the LLMApp
                response = await app.state.llmapp.ainvoke(
                    {"messages": input_message}, 
                    config=config
                )
                break  # Success, exit the retry loop
            except Exception as e:
                last_error = e
                logger.error(f"Error invoking LLMApp: {str(e)}")
                retry_count += 1
                
                if retry_count < max_retries:
                    # Wait before retrying
                    import asyncio
                    await asyncio.sleep(1 * retry_count)
                    
                    # Try to reinitialize the LLM app
                    if retry_count == max_retries - 1:
                        try:
                            from app.services.llm_service import create_llm_app
                            await create_llm_app(app)
                            logger.info("Reinitialized LLM application")
                        except Exception as reinit_error:
                            logger.error(f"Failed to reinitialize LLM app: {str(reinit_error)}")
        
        # If we exhausted all retries, return a friendly error
        if retry_count == max_retries and last_error:
            logger.error(f"Exhausted all retries: {str(last_error)}")
            return LLMResponse(
                content="I'm sorry, I encountered an issue while processing your request. Please try again later."
            )
        
        # Process the response from the LLM
        try:
            # Initialize empty lists for function calls and results
            function_calls = []
            function_results = []
            
            # Extract content from the response
            content = response.content if hasattr(response, "content") else "I couldn't generate a proper response."
            
            # Check for function calls in additional_kwargs
            if hasattr(response, "additional_kwargs"):
                # Handle multiple function call formats - first check for function_calls
                if "function_calls" in response.additional_kwargs:
                    # This is our standardized format from call_llm
                    func_calls = response.additional_kwargs.get("function_calls", [])
                    logger.info(f"Found standardized function_calls: {func_calls}")
                    
                    for func_call in func_calls:
                        function_call = FunctionCall(
                            name=func_call.get("name", ""),
                            arguments=func_call.get("arguments", {})
                        )
                        function_calls.append(function_call)
                
                # Next check for OpenAI format tool_calls
                elif "tool_calls" in response.additional_kwargs:
                    tool_calls = response.additional_kwargs.get("tool_calls", [])
                    logger.info(f"Found OpenAI-format tool_calls in additional_kwargs: {tool_calls}")
                    
                    for tool_call in tool_calls:
                        if isinstance(tool_call, dict):
                            # Check for Google/OpenAI format with function inside tool_call
                            if "function" in tool_call:
                                function_info = tool_call["function"]
                                function_name = function_info.get("name", "")
                                
                                # Parse arguments - could be string or dict
                                args_raw = function_info.get("arguments", "{}")
                                if isinstance(args_raw, str):
                                    try:
                                        args_dict = json.loads(args_raw)
                                    except json.JSONDecodeError:
                                        logger.error(f"Failed to parse arguments: {args_raw}")
                                        args_dict = {}
                                else:
                                    args_dict = args_raw
                                
                                function_call = FunctionCall(
                                    name=function_name,
                                    arguments=args_dict
                                )
                                function_calls.append(function_call)
                                
                                # Add the raw tool call to the response for client-side use
                                if "raw_tool_calls" not in response.additional_kwargs:
                                    response.additional_kwargs["raw_tool_calls"] = []
                                response.additional_kwargs["raw_tool_calls"].append(tool_call)
                
                # Finally check for single function_call (legacy format)
                elif "function_call" in response.additional_kwargs:
                    function_call_info = response.additional_kwargs.get("function_call", {})
                    logger.info(f"Found legacy function_call format: {function_call_info}")
                    
                    function_name = function_call_info.get("name", "")
                    args_raw = function_call_info.get("arguments", "{}")
                    
                    # Parse arguments - could be string or dict
                    if isinstance(args_raw, str):
                        try:
                            args_dict = json.loads(args_raw)
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse arguments: {args_raw}")
                            args_dict = {}
                    else:
                        args_dict = args_raw
                    
                    function_call = FunctionCall(
                        name=function_name,
                        arguments=args_dict
                    )
                    function_calls.append(function_call)
            
            # If we have function calls, execute them
            if function_calls:
                logger.info(f"Executing {len(function_calls)} function calls")
                
                # Get user role for authorization
                user_role = current_user.get("role") if current_user else "anonymous"
                
                for function_call in function_calls:
                    try:
                        # Log the function call attempt
                        logger.info(f"Executing function: {function_call.name} with args: {function_call.arguments}")
                        
                        # Execute the function
                        result = await function_router.execute_function(
                            function_call.name,
                            function_call.arguments,
                            user_role
                        )
                        
                        # Add the result
                        function_results.append(
                            FunctionResult(
                                name=function_call.name,
                                result=result
                            )
                        )
                        logger.info(f"Function {function_call.name} executed successfully")
                    except Exception as e:
                        logger.error(f"Error executing function {function_call.name}: {str(e)}")
                        function_results.append(
                            FunctionResult(
                                name=function_call.name,
                                result={"error": str(e)}
                            )
                        )
            
            # Return the response with function calls and results
            return LLMResponse(
                content=content,
                function_calls=function_calls if function_calls else None,
                function_results=function_results if function_results else None,
                raw_tool_calls=response.additional_kwargs.get("raw_tool_calls") if hasattr(response, "additional_kwargs") and "raw_tool_calls" in response.additional_kwargs else None
            )
            
        except Exception as process_error:
            logger.error(f"Error processing LLM response: {str(process_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing response: {str(process_error)}"
            )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )

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