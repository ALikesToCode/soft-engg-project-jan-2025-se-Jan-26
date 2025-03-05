from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import json
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.validators.llm_validator import LLMInputValidator
from app.services.function_router import function_router

# Initialize Gemini with function calling capability
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    convert_system_message_to_human=True
)

chat_history = []

# System message to help Gemini understand available functions
SYSTEM_PROMPT = """You are an AI assistant with access to various functions to help answer user queries.
When you need information, you can use these functions to get real-time data.
Always try to use the most relevant function for the task.
If you're unsure about data, use the appropriate function to fetch it rather than making assumptions."""

async def startNewChat():
    """Start a new chat session"""
    global chat_history
    chat_history = [SystemMessage(content=SYSTEM_PROMPT)]
    return True

class FunctionCall(BaseModel):
    """Schema for function calls made by Gemini"""
    name: str
    arguments: Dict[str, Any]

class LLMResponse(BaseModel):
    """Schema for LLM responses that may include function calls"""
    content: str
    function_calls: Optional[List[FunctionCall]] = None

router = APIRouter()

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
async def chat(request: LLMInputValidator):
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
        # Validate and sanitize input
        if not request.validate_schema_compliance():
            raise HTTPException(status_code=400, detail="Invalid input format")
        
        sanitized_query = request.sanitize_input()
        
        # Add user message to history
        chat_history.append(HumanMessage(content=sanitized_query))
        
        # Get available functions
        available_functions = function_router.get_function_declarations()
        
        # Generate response with function calling
        response = await llm.ainvoke(
            chat_history,
            tools=available_functions
        )
        
        # Process any function calls
        function_calls = []
        if hasattr(response, 'additional_kwargs') and 'tool_calls' in response.additional_kwargs:
            for tool_call in response.additional_kwargs['tool_calls']:
                # Execute the function
                function_name = tool_call['function']['name']
                function_args = json.loads(tool_call['function']['arguments'])
                
                result = await function_router.execute_function(function_name, function_args)
                
                # Add function call to response
                function_calls.append(FunctionCall(
                    name=function_name,
                    arguments=function_args
                ))
                
                # Add function result to chat history
                chat_history.append(AIMessage(content=str(result)))
        
        # Add AI response to history
        chat_history.append(AIMessage(content=response.content))
        
        return LLMResponse(
            content=response.content,
            function_calls=function_calls if function_calls else None
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating AI response: {str(e)}")

@router.get("/chat", 
    summary="Get chat history",
    description="Retrieves the current conversation history with the AI",
    response_description="List of messages in the conversation"
)
async def get_chat_history():
    """Get the current conversation history"""
    return [
        {
            "type": "system" if isinstance(msg, SystemMessage) else 
                   "human" if isinstance(msg, HumanMessage) else "ai",
            "content": msg.content
        }
        for msg in chat_history
    ]

@router.get("/available-functions",
    summary="Get available functions",
    description="Retrieves the list of functions available to the AI",
    response_description="List of function declarations"
)
async def get_available_functions():
    """Get all available functions that can be called by the AI"""
    return function_router.get_function_declarations()