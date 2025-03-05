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

When responding to users:
1. First, use your own knowledge and reasoning to think about the query
2. When you need real-time or specific information, use the appropriate function to fetch it
3. Combine your knowledge with function results to provide comprehensive responses
4. For current information or web content, use the web_search function
5. Always explain your reasoning and cite sources when using web search results

Remember that function calling doesn't replace your thinking - it enhances it. Provide thoughtful responses that combine your knowledge with function results.

Even when you call functions, you should still provide your own analysis and insights. Don't just return function results without adding your own understanding and context."""

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
        
        # Check for tool_calls format (newer LangChain format)
        if hasattr(response, 'additional_kwargs') and 'tool_calls' in response.additional_kwargs:
            for tool_call in response.additional_kwargs['tool_calls']:
                try:
                    # Extract function call details
                    function_name = tool_call['function']['name']
                    function_args = json.loads(tool_call['function']['arguments'])
                    
                    # Execute the function
                    result = await function_router.execute_function(function_name, function_args)
                    
                    # Add function call to response
                    function_calls.append(FunctionCall(
                        name=function_name,
                        arguments=function_args
                    ))
                    
                    # Add function result to chat history
                    function_result_msg = f"Function {function_name} returned: {json.dumps(result)}"
                    chat_history.append(AIMessage(content=function_result_msg))
                except Exception as e:
                    # Log the error but continue processing
                    print(f"Error executing function {function_name}: {str(e)}")
                    
                    # Add error message to chat history
                    error_msg = f"Error executing function {function_name}: {str(e)}"
                    chat_history.append(AIMessage(content=error_msg))
        
        # Check for function_call format (older format)
        elif hasattr(response, 'additional_kwargs') and 'function_call' in response.additional_kwargs:
            try:
                # Extract function call details
                function_call = response.additional_kwargs['function_call']
                function_name = function_call['name']
                
                # Parse arguments - handle both string and dict formats
                if isinstance(function_call['arguments'], str):
                    try:
                        function_args = json.loads(function_call['arguments'])
                    except json.JSONDecodeError:
                        function_args = {"raw_arguments": function_call['arguments']}
                else:
                    function_args = function_call['arguments']
                
                # Execute the function
                result = await function_router.execute_function(function_name, function_args)
                
                # Add function call to response
                function_calls.append(FunctionCall(
                    name=function_name,
                    arguments=function_args
                ))
                
                # Add function result to chat history
                function_result_msg = f"Function {function_name} returned: {json.dumps(result)}"
                chat_history.append(AIMessage(content=function_result_msg))
            except Exception as e:
                # Log the error but continue processing
                print(f"Error executing function {function_name}: {str(e)}")
                
                # Add error message to chat history
                error_msg = f"Error executing function {function_name}: {str(e)}"
                chat_history.append(AIMessage(content=error_msg))
            
        # If functions were called, generate a new response with the function results
        if function_calls:
            try:
                response = await llm.ainvoke(chat_history)
            except Exception as e:
                print(f"Error generating follow-up response: {str(e)}")
                # Continue with the original response if follow-up fails
        
        # Add AI response to history
        chat_history.append(AIMessage(content=response.content))
        
        # Ensure there's always meaningful content in the response
        response_content = response.content
        if not response_content.strip() and function_calls:
            # If content is empty but function calls were made, generate a detailed response
            # based on the function results
            if len(function_calls) == 1:
                function_name = function_calls[0].name
                function_args = function_calls[0].arguments
                
                # Get the function result from chat history
                function_result = None
                for msg in reversed(chat_history):
                    if isinstance(msg, AIMessage) and msg.content.startswith(f"Function {function_name} returned:"):
                        try:
                            result_str = msg.content.replace(f"Function {function_name} returned:", "").strip()
                            function_result = json.loads(result_str)
                            break
                        except:
                            pass
                
                # Generate a detailed response based on the function and its result
                if function_name == "get_courses":
                    if function_result and isinstance(function_result, list):
                        response_content = "Here are the available courses:\n\n"
                        for course in function_result:
                            title = course.get("title", "Untitled Course")
                            desc = course.get("description", "No description available")
                            course_id = course.get("id", "unknown")
                            response_content += f"• **{title}** ({course_id}): {desc}\n"
                        response_content += "\nYou can ask for more details about any specific course."
                    else:
                        response_content = "Here are the available courses. You can ask for more details about any specific course."
                
                elif function_name == "search_courses":
                    query = function_args.get("query", "")
                    if function_result and isinstance(function_result, list):
                        if len(function_result) > 0:
                            response_content = f"Here are the search results for '{query}':\n\n"
                            for course in function_result:
                                title = course.get("title", "Untitled Course")
                                desc = course.get("description", "No description available")
                                course_id = course.get("id", "unknown")
                                response_content += f"• **{title}** ({course_id}): {desc}\n"
                            response_content += "\nWould you like more information about any of these courses?"
                        else:
                            response_content = f"I couldn't find any courses matching '{query}'. Would you like to try a different search term?"
                    else:
                        response_content = f"Here are the search results for '{query}'. Would you like more information about any of these courses?"
                
                elif function_name == "get_course_details":
                    course_id = function_args.get("course_id", "")
                    if function_result:
                        title = function_result.get("title", "Untitled Course")
                        desc = function_result.get("description", "No description available")
                        credits = function_result.get("credits", "N/A")
                        instructor = function_result.get("instructor", "Not specified")
                        
                        response_content = f"## {title} ({course_id})\n\n"
                        response_content += f"**Description:** {desc}\n\n"
                        response_content += f"**Credits:** {credits}\n\n"
                        response_content += f"**Instructor:** {instructor}\n\n"
                        
                        if "prerequisites" in function_result:
                            prereqs = function_result.get("prerequisites", [])
                            if prereqs:
                                response_content += "**Prerequisites:**\n"
                                for prereq in prereqs:
                                    response_content += f"• {prereq}\n"
                        
                        response_content += "\nIs there anything specific about this course you'd like to know?"
                    else:
                        response_content = f"Here are the details for course {course_id}. Is there anything specific about this course you'd like to know?"
                
                elif function_name == "get_user_profile":
                    if function_result:
                        name = function_result.get("name", "User")
                        email = function_result.get("email", "Not available")
                        role = function_result.get("role", "Not specified")
                        
                        response_content = f"Here is your profile information:\n\n"
                        response_content += f"**Name:** {name}\n"
                        response_content += f"**Email:** {email}\n"
                        response_content += f"**Role:** {role}\n\n"
                        response_content += "Is there anything you'd like to update in your profile?"
                    else:
                        response_content = "Here is your profile information. Is there anything you'd like to update?"
                
                elif function_name.startswith("get_"):
                    response_content = f"Here is the information you requested. Is there anything specific you'd like to know about this data?"
                
                else:
                    response_content = f"The operation was completed successfully. Is there anything else you'd like to do?"
            
            else:
                # Multiple function calls
                response_content = "I've gathered the information you requested. Here are the results:"
                for i, func_call in enumerate(function_calls):
                    response_content += f"\n\n{i+1}. Information from {func_call.name}"
                response_content += "\n\nIs there anything specific you'd like to know about these results?"
        
        return LLMResponse(
            content=response_content,
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

@router.post("/execute-function",
    summary="Execute a function",
    description="Executes a function with the provided arguments",
    response_description="Result of the function execution"
)
async def execute_function(request: LLMInputValidator):
    """
    Execute a function with the provided arguments
    
    This endpoint processes the user's message and returns the result of the function execution.
    
    Args:
        request: The validated LLM request containing the function name and arguments
        
    Returns:
        Result of the function execution
    """
    try:
        # Validate and sanitize input
        if not request.validate_schema_compliance():
            raise HTTPException(status_code=400, detail="Invalid input format")
        
        sanitized_query = request.sanitize_input()
        
        # Get available functions
        available_functions = function_router.get_function_declarations()
        
        # Find the function to execute
        function_to_execute = None
        for func in available_functions:
            if func['name'] == sanitized_query:
                function_to_execute = func
                break
        
        if not function_to_execute:
            raise HTTPException(status_code=400, detail="Function not found")
        
        # Execute the function
        result = await function_router.execute_function(sanitized_query, function_to_execute['arguments'])
        
        return {
            "result": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing function: {str(e)}")