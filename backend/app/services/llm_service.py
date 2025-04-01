import os
import logging
import json
from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.services.function_router import function_router

logger = logging.getLogger(__name__)

# Initialize chat model
def get_llm(functions=None):
    """Get the LLM model instance with function calling enabled"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0,  # Use lower temperature for more deterministic function calling
        convert_system_message_to_human=True,  # Required for function calling
        tools=functions,  # Pass the function definitions to the model
    )

# System message to help the LLM understand available functions
def get_system_prompt():
    """Get the system prompt for the LLM with instructions about function usage"""
    return """You are a helpful AI assistant for an educational platform. 
You have access to functions that you can call to retrieve information or perform actions.

When a user asks a question that requires using these functions, you should call the appropriate function.
Respond directly to simple questions that don't require function calls.
Always be helpful, concise, and professional."""

async def call_llm(messages):
    """Function to call the LLM model with the provided messages and handle function calling"""
    # Get function declarations for the LLM
    functions = function_router.get_function_declarations()
    
    # Format functions for Gemini
    formatted_functions = []
    for func in functions:
        formatted_func = {
            "name": func["name"],
            "description": func["description"],
            "parameters": func["parameters"]
        }
        formatted_functions.append(formatted_func)
    
    # Get the LLM with functions enabled
    llm = get_llm(formatted_functions)
    
    # Create prompt template with system message and user messages
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=get_system_prompt()),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    # Apply the prompt template to the current state
    prompt = await prompt_template.ainvoke({"messages": messages})
    
    # Call the LLM with the prompt
    response = await llm.ainvoke(prompt)
    
    logger.debug(f"LLM response: {response}")
    
    # Check for function calls in the response
    function_calls = []
    if hasattr(response, 'additional_kwargs') and 'tool_calls' in response.additional_kwargs:
        tool_calls = response.additional_kwargs.get('tool_calls', [])
        for tool_call in tool_calls:
            try:
                function_call = {
                    "name": tool_call.get('function', {}).get('name'),
                    "arguments": json.loads(tool_call.get('function', {}).get('arguments', '{}'))
                }
                function_calls.append(function_call)
            except Exception as e:
                logger.error(f"Error parsing function call: {e}")
    
    # Add function calls to response
    if function_calls:
        response.additional_kwargs['function_calls'] = function_calls
    
    return response

class LLMApp:
    """Simple LLM application class to replace LangGraph"""
    
    def __init__(self):
        self.conversations = {}
        
    async def ainvoke(self, state, config=None):
        """Process a message and return a response with potential function calls"""
        messages = state.get("messages", [])
        thread_id = config.get("configurable", {}).get("thread_id", "default") if config else "default"
        
        # Retrieve existing conversation or start a new one
        conversation = self.conversations.get(thread_id, [])
        
        # Add new messages to the conversation
        conversation.extend(messages)
        
        # Get response from LLM
        response = await call_llm(conversation)
        
        # Update the conversation with the response
        conversation.append(response)
        
        # Store updated conversation
        self.conversations[thread_id] = conversation
        
        # Return updated state with function calls if present
        return response
    
    async def aget_state(self, config=None):
        """Get the current state of a conversation"""
        thread_id = config.get("configurable", {}).get("thread_id", "default") if config else "default"
        conversation = self.conversations.get(thread_id, [])
        return [{"messages": conversation}]

async def create_llm_app(app):
    """Initialize a simple LLM application
    
    Args:
        app: FastAPI application instance
    """
    logger.info("Initializing LLM application")
    
    # Create a new LLMApp instance
    llm_app = LLMApp()
    
    # Store the initialized app in application state
    app.state.llmapp = llm_app
    
    logger.info("LLM application initialized successfully")
    return llm_app
