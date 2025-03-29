from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
import json
from typing import List, Dict, Any, Optional
import os

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.validators.llm_validator import LLMInputValidator
from app.services.function_router import function_router

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
                                "name": "get_courses",
                                "arguments": {"category": "all"}
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
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Use the app state to get the LLMApp
        app = req.app
        
        if not hasattr(app.state, "llmapp"):
            raise HTTPException(
                status_code=500, 
                detail="LLMApp not initialized. Server configuration issue."
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
                if "connection" in error_str or "closed" in error_str or "pool" in error_str:
                    logger.warning(f"Database connection error (attempt {retry_count+1}/{max_retries}): {str(e)}")
                    retry_count += 1
                    
                    # If this appears to be a connection pool issue, try to reinitialize
                    if retry_count == max_retries - 1 and hasattr(app.state, "pool"):
                        try:
                            # Attempt to recreate the connection
                            import asyncio
                            await asyncio.sleep(1)  # Brief pause before retrying
                            logger.info("Attempting to refresh connection pool")
                        except Exception as pool_error:
                            logger.error(f"Failed to refresh connection pool: {str(pool_error)}")
                else:
                    # Not a connection error, no need to retry
                    raise e
        
        # If we've exhausted all retries
        if retry_count >= max_retries:
            logger.error(f"Failed after {max_retries} attempts: {str(last_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Database connection error after multiple attempts: {str(last_error)}"
            )
        
        # Extract the last message (AI response)
        ai_message = response["messages"][-1]
        
        # Process function calls if present and execute them
        function_calls = []
        function_results = []
        
        if hasattr(ai_message, "additional_kwargs"):
            # Process tool_calls format (newer LangChain format)
            if "tool_calls" in ai_message.additional_kwargs:
                for tool_call in ai_message.additional_kwargs["tool_calls"]:
                    function_name = tool_call["function"]["name"]
                    try:
                        arguments = json.loads(tool_call["function"]["arguments"])
                    except:
                        arguments = {"query_text": tool_call["function"]["arguments"]}
                        
                    # Add to function calls list
                    function_calls.append(FunctionCall(
                        name=function_name,
                        arguments=arguments
                    ))
                    
                    # Execute function and capture result
                    try:
                        result = await function_router.execute_function(function_name, arguments)
                        function_results.append({
                            "name": function_name,
                            "result": result
                        })
                    except Exception as e:
                        function_results.append({
                            "name": function_name,
                            "error": str(e)
                        })
                        
            # Process function_call format (older format)
            elif "function_call" in ai_message.additional_kwargs:
                fc = ai_message.additional_kwargs["function_call"]
                function_name = fc["name"]
                try:
                    arguments = json.loads(fc["arguments"])
                except:
                    arguments = {"query_text": fc["arguments"]}
                    
                # Add to function calls list
                function_calls.append(FunctionCall(
                    name=function_name,
                    arguments=arguments
                ))
                
                # Execute function and capture result
                try:
                    result = await function_router.execute_function(function_name, arguments)
                    function_results.append({
                        "name": function_name,
                        "result": result
                    })
                except Exception as e:
                    function_results.append({
                        "name": function_name,
                        "error": str(e)
                    })
        
        # If we have function results, send them back to the LLM for a better response
        if function_results:
            # Add function results to the conversation
            for fr in function_results:
                if "error" in fr:
                    result_msg = f"Error executing function {fr['name']}: {fr['error']}"
                else:
                    result_msg = f"Function {fr['name']} returned: {json.dumps(fr['result'])}"
                response["messages"].append(AIMessage(content=result_msg))
            
            # Get a new response from the LLM with the function results
            followup_response = await app.state.llmapp.ainvoke(
                response,
                config=config
            )
            
            # Use the updated response
            updated_ai_message = followup_response["messages"][-1]
            
            # Return the updated response
            return LLMResponse(
                content=updated_ai_message.content,
                function_calls=function_calls if function_calls else None
            )
                
        # Return the original response if no functions were called
        return LLMResponse(
            content=ai_message.content,
            function_calls=function_calls if function_calls else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
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