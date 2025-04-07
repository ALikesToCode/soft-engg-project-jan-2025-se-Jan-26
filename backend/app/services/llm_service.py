import os
import logging
import json
import time
import requests
from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.services.function_router import function_router

logger = logging.getLogger(__name__)

# Available models cache to avoid repeated API calls
_available_models_cache = None

def get_available_models():
    """Get a list of available models from the Gemini API"""
    global _available_models_cache
    
    # Hard-coded list of commonly available models for fast path
    common_models = [
        "gemini-1.5-pro-latest", 
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro", 
        "gemini-1.5-flash",
        "gemini-2.0-pro", 
        "gemini-2.0-flash",
        "gemini-1.0-pro"
    ]
    
    # Return cached models if available
    if _available_models_cache is not None:
        return _available_models_cache
    
    try:
        # Get API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("No Google API key found, using common models list")
            return common_models
        
        # Call models endpoint
        url = "https://generativelanguage.googleapis.com/v1beta/models"
        headers = {"x-goog-api-key": api_key}
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code != 200:
            logger.warning(f"Failed to fetch models, status code: {response.status_code}, using common models")
            return common_models
        
        # Parse response
        data = response.json()
        
        # Filter for chat models
        models = [
            model["name"].split("/")[-1] 
            for model in data.get("models", []) 
            if "gemini" in model.get("name", "").lower() and model.get("supportedGenerationMethods", []) and "generateContent" in model.get("supportedGenerationMethods", [])
        ]
        
        # Cache results
        _available_models_cache = models
        
        # Log available models
        logger.info(f"Available models: {models}")
        
        return models
    except Exception as e:
        logger.error(f"Error fetching models: {str(e)}")
        return common_models

def get_system_prompt():
    """Get the system prompt for the LLM
    
    This is used to set the behavior and tone of the AI assistant.
    """
    return """
You are an AI learning assistant for a university learning management system.
Your primary role is to help students, faculty, and support staff with their educational needs.
don't give answers that are not related to the provided context.
You are educator don't give answers that are not related to the provided context.
You are not a chatbot, you are an educator.

whenever students tries to ask you questions about the course, lecture, or anything related to the course, You should answer ensuring that the answer is related to the course and the lecture.
and also make sure that answer is not giving Graded assignemnt questions or anything related to the course content.
You should always guide the students to the course website to answer their questions.
You should not give direct answers to the students, you should always guide them to the course website to answer their questions.
Not answer questions that are not related to the course or the lecture.
Not answer questions that are not related to technology. 
You can answer question related to maths, science, computer science.

CAPABILITIES:
- Answer questions about courses, assignments, and academic materials
- Provide learning support and explanations of complex topics
- Help faculty manage their courses
- Assist support staff with administrative tasks
- Execute functions to retrieve or modify data when necessary

BEHAVIOR GUIDELINES:
- Be helpful, respectful, and educational in tone
- Provide accurate information and admit when you don't know something
- When the answer requires domain-specific knowledge, use your general knowledge and clearly indicate limitations
- Respect academic integrity - never complete assignments for students or write essays on their behalf
- Use function calling when appropriate to retrieve or update information
- Protect user privacy by not sharing one user's information with another
- Generate thoughtful, nuanced responses that are appropriate for an educational context
- Focus on being helpful while maintaining appropriate educational boundaries

When accessing information, use the available tools and functions that have been provided to you.
"""

# Initialize chat model
def get_llm(functions=None, use_fallback=False, use_grounding=True):
    """Get the LLM model instance with function calling enabled
    
    Args:
        functions: List of function declarations to pass to the model
        use_fallback: Whether to use the fallback model (gemini-2.0-flash)
        use_grounding: Whether to enable grounding capabilities
        
    Returns:
        LLM instance configured with the appropriate model
    """
    # Format tools for Gemini API via LangChain
    tools = []
    
    # Add function tools if provided
    if functions:
        # Ensure functions are in the OpenAI-compatible format expected by the Gemini API
        # Each function should be an object with "type": "function" and a nested "function" object
        for func in functions:
            # Check if the function is already in the correct format
            if isinstance(func, dict) and "type" in func and func.get("type") == "function":
                tools.append(func)
            else:
                # Convert to OpenAI-compatible format
                formatted_func = {
                    "type": "function",
                    "function": {
                        "name": func["name"],
                        "description": func["description"],
                        "parameters": func["parameters"]
                    }
                }
                tools.append(formatted_func)
    
    # Add grounding tool if enabled
    if use_grounding:
        logger.info("Enabling grounding with Google Search")
        tools.append({"google_search": {}})
    
    # Get available models
    available_models = get_available_models()
    logger.info(f"All available models: {available_models}")
    
    # Model selection logic
    if use_fallback:
        preferred_models = ["gemini-2.0-pro", "gemini-2.0-flash", "gemini-1.5-pro-latest", "gemini-1.5-flash-latest"]
    else:
        preferred_models = ["gemini-2.0-pro", "gemini-1.5-pro-latest", "gemini-1.5-pro", "gemini-2.0-flash"]
    
    # Find the best available model
    model_name = next((model for model in preferred_models if model in available_models), "gemini-1.5-flash")
    logger.info(f"Selected model: {model_name}")
    
    # Configure model parameters
    model_kwargs = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
    }
    
    # Create LLM instance
    try:
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            safety_settings={
                "HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
                "HATE": "BLOCK_MEDIUM_AND_ABOVE",
                "SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
                "DANGEROUS": "BLOCK_MEDIUM_AND_ABOVE"
            },
            convert_system_message_to_human=False,
            tools=tools if tools else None,
            streaming=False,
            **model_kwargs
        )
    except Exception as e:
        logger.error(f"Error creating LLM instance: {str(e)}")
        # Fallback to simpler configuration
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

# Store loaded LLM instances for reuse
_llm_cache = {}

async def call_llm(messages, use_fallback=False, use_grounding=True):
    """Function to call the LLM model with the provided messages and handle function calling"""
    # Get function declarations for the LLM
    functions = function_router.get_function_declarations()
    
    # Format functions correctly for Gemini API OpenAI compatibility
    if not hasattr(call_llm, '_formatted_functions'):
        formatted_functions = []
        for func in functions:
            # Use OpenAI-compatible format with type:function
            formatted_func = {
                "type": "function",
                "function": {
                    "name": func["name"],
                    "description": func["description"],
                    "parameters": func["parameters"]
                }
            }
            formatted_functions.append(formatted_func)
        call_llm._formatted_functions = formatted_functions
    else:
        formatted_functions = call_llm._formatted_functions
    
    # Create a cache key based on the model settings - fixed with local variables
    cache_key = f"primary_grounding_{use_grounding}" if not use_fallback else f"fallback_grounding_{use_grounding}"
    
    # Try with the primary model first
    try:
        # Check if we have a cached LLM instance
        if cache_key not in _llm_cache:
            # Create and cache the LLM
            logger.info(f"Creating new LLM instance with cache key: {cache_key}")
            _llm_cache[cache_key] = get_llm(formatted_functions, use_fallback=use_fallback, use_grounding=use_grounding)
        else:
            logger.info(f"Using cached LLM instance with key: {cache_key}")
        
        # Get the cached LLM
        llm = _llm_cache[cache_key]
        
        # Get cached prompt template if available, create it otherwise
        if not hasattr(call_llm, '_prompt_template'):
            prompt_template = ChatPromptTemplate.from_messages([
                SystemMessage(content=get_system_prompt()),
                MessagesPlaceholder(variable_name="messages")
            ])
            call_llm._prompt_template = prompt_template
            logger.info("Created new prompt template")
        else:
            prompt_template = call_llm._prompt_template
            logger.info("Using cached prompt template")
        
        # Apply the prompt template to the current state (this can't be cached as messages change)
        prompt = await prompt_template.ainvoke({"messages": messages})
        
        # Call the LLM with the prompt
        start_time = time.time()
        logger.info("Sending request to LLM...")
        response = await llm.ainvoke(prompt)
        elapsed = time.time() - start_time
        logger.info(f"LLM response received in {elapsed:.2f} seconds")
        
        # Check for grounding evidence in the response
        has_grounding = False
        if hasattr(response, 'additional_kwargs') and 'grounding' in str(response.additional_kwargs):
            has_grounding = True
            logger.info("Grounding information detected in response")
        
        logger.info(f"Grounding enabled: {use_grounding}, Grounding detected: {has_grounding}")
        
    except Exception as e:
        logger.warning(f"Primary model failed: {str(e)}. Falling back to secondary model")
        
        # Try the fallback model
        try:
            # Check if we have a cached fallback LLM instance
            fallback_key = "fallback_grounding_true"
            if fallback_key not in _llm_cache:
                # Create and cache the fallback LLM
                logger.info("Creating new fallback LLM instance")
                _llm_cache[fallback_key] = get_llm(formatted_functions, use_fallback=True, use_grounding=True)
            else:
                logger.info("Using cached fallback LLM instance")
            
            # Get the cached fallback LLM
            llm_fallback = _llm_cache[fallback_key]
            
            # Use the same prompt template as before
            prompt_template = call_llm._prompt_template
            prompt = await prompt_template.ainvoke({"messages": messages})
            
            # Call the fallback LLM
            start_time = time.time()
            logger.info("Sending request to fallback LLM...")
            response = await llm_fallback.ainvoke(prompt)
            elapsed = time.time() - start_time
            logger.info(f"Fallback LLM response received in {elapsed:.2f} seconds")
            
            # Check for grounding evidence in fallback response
            has_grounding = False
            if hasattr(response, 'additional_kwargs') and 'grounding' in str(response.additional_kwargs):
                has_grounding = True
                logger.info("Grounding information detected in fallback response")
            
            logger.info(f"Fallback grounding enabled: {use_grounding}, Grounding detected: {has_grounding}")
            
        except Exception as fallback_error:
            logger.error(f"Fallback model also failed: {str(fallback_error)}")
            raise
    
    # Process tool/function calls from the response
    function_calls = []
    
    # Check for any function calls in the response
    if hasattr(response, 'additional_kwargs'):
        additional_kwargs = response.additional_kwargs
        
        # Process function calls from tool_calls
        if 'tool_calls' in additional_kwargs:
            tool_calls = additional_kwargs['tool_calls']
            
            for tool_call in tool_calls:
                if 'function' in tool_call:
                    func_call = tool_call['function']
                    name = func_call.get('name', '')
                    arguments = {}
                    
                    # Parse arguments (sometimes they come as a string, sometimes as a dict)
                    args = func_call.get('arguments', {})
                    if isinstance(args, str):
                        try:
                            arguments = json.loads(args)
                        except json.JSONDecodeError:
                            logger.warning(f"Could not parse function arguments: {args}")
                            arguments = {}
                    else:
                        arguments = args
                    
                    # Add to list of function calls
                    function_calls.append({
                        "name": name,
                        "arguments": arguments
                    })
                    
                    logger.info(f"Extracted function call: {name}")
            
            # Store raw tool calls for debugging
            response.additional_kwargs['raw_tool_calls'] = tool_calls
    
    # Add function calls to response if any were found
    if function_calls:
        response.additional_kwargs['function_calls'] = function_calls
        logger.info(f"Added {len(function_calls)} function calls to response")
    
    return response

class LLMApp:
    """Simple LLM application class to replace LangGraph"""
    
    def __init__(self):
        self.conversations = {}
        
    async def ainvoke(self, state, config=None):
        """Process a message and return a response with potential function calls"""
        messages = state.get("messages", [])
        thread_id = config.get("configurable", {}).get("thread_id", "default") if config else "default"
        
        # Extract model options if provided in config
        options = config.get("configurable", {}).get("model_options", {}) if config else {}
        use_fallback = options.get("use_fallback", False)
        use_grounding = options.get("use_grounding", True)
        
        # Retrieve existing conversation or start a new one
        conversation = self.conversations.get(thread_id, [])
        
        # Add new messages to the conversation
        conversation.extend(messages)
        
        # Get response from LLM with specified options
        try:
            response = await call_llm(
                conversation, 
                use_fallback=use_fallback, 
                use_grounding=use_grounding
            )
            
            # Update the conversation with the response
            conversation.append(response)
            
            # Store updated conversation
            self.conversations[thread_id] = conversation
            
            # Return response
            return response
            
        except Exception as e:
            logger.error(f"Error in LLMApp.ainvoke: {str(e)}")
            # Return error as a message
            return AIMessage(content=f"I'm sorry, I encountered an error: {str(e)}")
    
    async def aget_state(self, config=None):
        """Get the current state of a conversation"""
        thread_id = config.get("configurable", {}).get("thread_id", "default") if config else "default"
        conversation = self.conversations.get(thread_id, [])
        return [{"messages": conversation}]
    
    def clear_conversation(self, thread_id="default"):
        """Clear a specific conversation"""
        if thread_id in self.conversations:
            self.conversations[thread_id] = []
            return True
        return False

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
