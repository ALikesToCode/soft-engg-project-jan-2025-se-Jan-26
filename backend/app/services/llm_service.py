import os
import logging
from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import START, StateGraph, MessagesState
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

async def call_llm(state: MessagesState):
    """Function to call the LLM model with the current state"""
    # Get the LLM and prompt template
    llm = get_llm()
    
    # Create prompt template with system message and user messages
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", get_system_prompt()),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    # Apply the prompt template to the current state
    prompt = await prompt_template.ainvoke(state)
    
    # Call the LLM with the prompt
    response = await llm.ainvoke(prompt)
    
    # Return the updated state with the new response
    return {"messages": state["messages"] + [response]}

async def create_llm_app(app):
    """Initialize the LLM application with LangGraph
    
    Args:
        app: FastAPI application instance
    """
    logger.info("Initializing LLM application")
    
    # Check if we have a checkpointer configured in the app state
    if not hasattr(app.state, "checkpointer") or not app.state.checkpointer:
        logger.error("Cannot initialize LLMApp: missing checkpointer in app state")
        raise ValueError("Missing checkpointer in app state")
    
    # Create a new state graph for conversations
    builder = StateGraph(MessagesState)
    
    # Add the LLM node to the graph
    builder.add_node("llm", call_llm)
    
    # Set up the graph flow: START -> llm -> END
    builder.set_entry_point("llm")
    
    # Compile the graph
    graph = builder.compile()
    
    # Configure persistence with the checkpointer
    memory = await graph.with_checkpointer(
        app.state.checkpointer,
        key="conversation_history"
    ).aconfigure(
        configurable={
            "thread_id": "default"  # Default thread ID
        }
    )
    
    # Store the initialized app in application state
    app.state.llmapp = memory
    
    logger.info("LLM application initialized successfully")
    return memory
