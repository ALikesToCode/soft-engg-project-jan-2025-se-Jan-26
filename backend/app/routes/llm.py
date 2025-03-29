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
from app.utils.openapi import get_openapi
from app.routes.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

# Initialize chat model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# System message to help Gemini understand available functions
prompt = """You are an AI assistant with access to various functions to help answer user queries.

When responding to users:
1. First, use your own knowledge and reasoning to think about the query
2. When you need real-time or specific information, use the appropriate function to fetch it
3. Combine your knowledge with function results to provide comprehensive responses
4. For current information or web content, use the web_search function
5. Always explain your reasoning and cite sources when using web search results
6. When asked about Software Engineering course materials, use the query_course_materials function to retrieve relevant information from the course PDFs

Remember that function calling doesn't replace your thinking - it enhances it. Provide thoughtful responses that combine your knowledge with function results.

Even when you call functions, you should still provide your own analysis and insights. Don't just return function results without adding your own understanding and context."""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
prompt_template = ChatPromptTemplate.from_messages(
    [   ("system", prompt),
        MessagesPlaceholder(variable_name="messages")
    ]
)

from langgraph.graph import START, MessagesState, StateGraph
async def call_llm(state: MessagesState):
    prompt = await prompt_template.ainvoke(state)
    response = await llm.ainvoke(prompt)
    return {"messages": state["messages"] + [response]}

# LangGraph lifecycle setup
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from contextlib import asynccontextmanager

# Global variables for LangGraph
checkpointer = None
llmapp = None

router = APIRouter()

from pydantic import BaseModel
class LLMRequest(BaseModel):
    id: str
    query: str

class FunctionCall(BaseModel):
    """Schema for function calls made by Gemini"""
    name: str
    arguments: Dict[str, Any]

class LLMResponse(BaseModel):
    """Schema for LLM responses that may include function calls"""
    content: str
    function_calls: Optional[List[FunctionCall]] = None

# Vector store retrieval function
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def get_vector_store():
    """Get initialized vector store connection"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
            
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name="vector_store",
            connection_string=database_url
        )
        return vector_store
    except Exception as e:
        print(f"Error initializing vector store: {str(e)}")
        return None

async def query_vector_store(query_text, k=3):
    """Query the vector store for relevant documents"""
    vector_store = get_vector_store()
    if not vector_store:
        return []
    
    docs = vector_store.similarity_search(query_text, k=k)
    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page", 0)
        }
        for doc in docs
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
                        ]
                    }
                }
            }
        },
        400: {"description": "Invalid input"},
        500: {"description": "Server error during AI processing"}
    }
)
async def chat(request: LLMRequest, req: Request):
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
                    if hasattr(app.state, "pool") and app.state.pool:
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
        
        # Attempt to invoke the LLMApp with retry logic for connection issues
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
                error_str = str(e).lower()
                
                # Check if this is a connection issue
                if "connection" in error_str or "closed" in error_str or "pool" in error_str or "bad" in error_str or "discarding" in error_str:
                    logger.warning(f"Database connection error (attempt {retry_count+1}/{max_retries}): {str(e)}")
                    retry_count += 1
                    
                    # If this appears to be a connection pool issue, try to reinitialize
                    if hasattr(app.state, "pool"):
                        try:
                            # Attempt to refresh the connection
                            import asyncio
                            await asyncio.sleep(1 * retry_count)  # Exponential backoff
                            logger.info("Attempting to refresh connection pool")
                            
                            # Get a connection to test if pool is healthy
                            async with app.state.pool.connection() as conn:
                                await conn.execute("SELECT 1")
                                logger.info("Connection pool test successful")
                        except Exception as pool_error:
                            logger.error(f"Failed to refresh connection pool: {str(pool_error)}")
                            
                            # On last retry attempt, try to recreate the pool
                            if retry_count == max_retries - 1 and hasattr(app.state, "pool"):
                                try:
                                    # Close the existing pool
                                    logger.warning("Attempting to recreate connection pool")
                                    await app.state.pool.close()
                                    
                                    # Get the original connection string
                                    connection_string = os.getenv("DATABASE_URL")
                                    if "postgresql+asyncpg://" in connection_string:
                                        connection_string = connection_string.replace("postgresql+asyncpg://", "postgresql://")
                                    
                                    # Create a new pool
                                    app.state.pool = AsyncConnectionPool(connection_string)
                                    
                                    # Recreate the checkpointer
                                    app.state.checkpointer = AsyncPostgresSaver(pool=app.state.pool)
                                    
                                    # Recreate the LLMApp
                                    await create_llm_app(app)
                                    logger.info("Successfully recreated connection pool and LLMApp")
                                except Exception as recreate_error:
                                    logger.error(f"Failed to recreate connection pool: {str(recreate_error)}")
                else:
                    # Not a connection error, break the loop
                    logger.error(f"Non-connection error in LLMApp: {str(e)}")
                    break
        
        # If we exhausted all retries, raise the last error
        if retry_count == max_retries and last_error:
            logger.error(f"Exhausted all retries: {str(last_error)}")
            # Return a "friendly" error response instead of crashing
            return LLMResponse(
                content="I'm sorry, I encountered an issue while processing your request. Please try again later."
            )
        
        # Format and return the response
        if "messages" in response and len(response["messages"]) > 0:
            output_message = response["messages"][-1]
            
            if output_message is None or not hasattr(output_message, "content"):
                return LLMResponse(
                    content="I'm sorry, I couldn't generate a response. Please try again."
                )
            
            # Check if we need to convert legacy function calls format
            function_calls = []
            if hasattr(output_message, "additional_kwargs") and "function_calls" in output_message.additional_kwargs:
                raw_function_calls = output_message.additional_kwargs["function_calls"]
                
                # Convert to our function call format
                for fc in raw_function_calls:
                    # Parse arguments from string to dict if needed
                    args = fc.get("arguments", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except:
                            # If we can't parse it, use it as is
                            logger.warning(f"Could not parse function arguments: {args}")
                            
                    function_calls.append({
                        "name": fc.get("name", "unknown_function"),
                        "arguments": args
                    })
            
            # Handle tool calls format for newer Google Gemini models
            if hasattr(output_message, "tool_calls") and output_message.tool_calls:
                for tool_call in output_message.tool_calls:
                    # Extract function details
                    name = tool_call.get("name", "unknown_function")
                    args = tool_call.get("args", {})
                    
                    # Convert args from string to dict if needed
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except:
                            logger.warning(f"Could not parse tool call arguments: {args}")
                    
                    function_calls.append({
                        "name": name,
                        "arguments": args
                    })
                    
            # If function name format needs conversion (e.g., get_courses -> getCourses)
            for fc in function_calls:
                # Convert snake_case to camelCase if needed
                if "_" in fc["name"]:
                    parts = fc["name"].split("_")
                    camel_case = parts[0] + ''.join(x.title() for x in parts[1:])
                    
                    # Check if camelCase version exists in our function declarations
                    function_names = [f["name"] for f in function_router.get_function_declarations()]
                    if camel_case in function_names:
                        fc["name"] = camel_case
            
            return LLMResponse(
                content=output_message.content,
                function_calls=function_calls if function_calls else None
            )
        else:
            return LLMResponse(
                content="I apologize, but I couldn't generate a proper response."
            )
            
    except Exception as e:
        logger.error(f"Unhandled error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
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
    
    if not hasattr(app.state, "pool"):
        raise HTTPException(
            status_code=500, 
            detail="Database pool not initialized. Server configuration issue."
        )
    
    async with app.state.pool.connection() as conn:
        async with conn.cursor() as cursor:
            try:
                await cursor.execute("DELETE FROM checkpoints WHERE thread_id = %s", (id,))
                await cursor.execute("DELETE FROM checkpoint_writes WHERE thread_id = %s", (id,))
                await cursor.execute("DELETE FROM checkpoint_blobs WHERE thread_id = %s", (id,))
                return {"message": f"Chat history for thread_id '{id}' has been cleared."}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error clearing chat history: {e}")

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