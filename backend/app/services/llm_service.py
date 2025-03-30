import os
import logging
from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.services.function_router import function_router

logger = logging.getLogger(__name__)

# Initialize chat model
def get_llm():
    """Get the LLM model instance"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

# System message to help the LLM understand available functions
def get_system_prompt():
    """Get the system prompt for the LLM with tool/function descriptions"""
    # Get function declarations for the LLM
    tools = function_router.get_function_declarations()
    
    # Create a system prompt that includes function definitions
    functions_desc = "\n\n".join([
        f"Function: {tool['name']}\nDescription: {tool['description']}\nParameters: {tool['parameters']}"
        for tool in tools
    ])
    
    return f"""You are a helpful AI assistant for an educational platform. 
You have access to the following functions that you can call:

{functions_desc}

When a user asks a question that requires using these functions, call the appropriate function.
Respond directly to simple questions that don't require function calls.
Always be helpful, concise, and professional."""

async def call_llm(messages):
    """Function to call the LLM model with the provided messages"""
    # Get the LLM and prompt template
    llm = get_llm()
    
    # Create prompt template with system message and user messages
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=get_system_prompt()),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    # Apply the prompt template to the current state
    prompt = await prompt_template.ainvoke({"messages": messages})
    
    # Call the LLM with the prompt
    response = await llm.ainvoke(prompt)
    
    return response

class LLMApp:
    """Simple LLM application class to replace LangGraph"""
    
    def __init__(self):
        self.conversations = {}
        
    async def ainvoke(self, state, config=None):
        """Process a message and return a response"""
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
        
        # Return updated state
        return {"messages": conversation}
    
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
