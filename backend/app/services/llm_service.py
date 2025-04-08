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
        "gemini-2.0-flash", 
        "gemini-1.0-pro"
    ]
    
    # Return cached models if available
    if _available_models_cache is not None:
        return _available_models_cache
    
    # Try fast path first - if we can't connect to the API, use common models
    try:
        # Check if model list was cached on disk
        cache_path = os.path.join(os.path.dirname(__file__), "model_cache.json")
        cache_expiry = 3600  # Cache validity in seconds (1 hour)
        
        # Check for valid cache file
        if os.path.exists(cache_path):
            file_age = time.time() - os.path.getmtime(cache_path)
            if file_age < cache_expiry:
                try:
                    with open(cache_path, 'r') as f:
                        cached_data = json.load(f)
                        _available_models_cache = cached_data.get('models', common_models)
                        logger.info(f"Using cached model list ({len(_available_models_cache)} models)")
                        return _available_models_cache
                except (json.JSONDecodeError, IOError):
                    logger.warning("Failed to read model cache file")
        
        # If no valid cache, fetch from API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY not found in environment")
            _available_models_cache = common_models
            return common_models
        
        # Call the models.list API endpoint with timeout
        url = "https://generativelanguage.googleapis.com/v1beta/models"
        response = requests.get(url, params={"key": api_key}, timeout=2.0)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract model names from response
            models = [model.get("name", "").split("/")[-1] for model in data.get("models", [])]
            
            # Filter to include only Gemini models
            gemini_models = [model for model in models if model.startswith("gemini")]
            
            if gemini_models:
                logger.info(f"Available Gemini models: {len(gemini_models)} models")
                # Cache the results
                _available_models_cache = gemini_models
                
                # Write to cache file
                try:
                    with open(cache_path, 'w') as f:
                        json.dump({'models': gemini_models}, f)
                except IOError:
                    logger.warning("Failed to write model cache file")
                
                return gemini_models
            else:
                logger.warning("No Gemini models found in API response")
                _available_models_cache = common_models
                return common_models
        else:
            logger.error(f"Failed to get models: {response.status_code} - {response.text}")
            _available_models_cache = common_models
            return common_models
    except Exception as e:
        logger.warning(f"Error getting available models: {str(e)}, using default list")
        _available_models_cache = common_models
        return common_models

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
    
    # Define model preferences - updated with newest experimental models first
    preferred_models = [
        # Try newest experimental/preview models first
        "gemini-2.5-pro-preview",  # Try 2.5 Preview first
        "gemini-2.0-pro-exp",      # Then 2.0 Pro Experimental
        "gemini-exp-",             # Any experimental models 
        "gemini-2.0-flash",        # Then 2.0 Flash
        "gemini-1.5-pro-latest",   # Then 1.5 models  
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro", 
        "gemini-1.5-flash"
    ]
    
    fallback_models = [
        "gemini-2.0-flash",  # Primary fallback
        "gemini-1.5-flash-latest",  # Secondary fallback
        "gemini-1.0-pro"  # Last resort fallback
    ]
    
    # Select model based on availability
    model_candidates = fallback_models if use_fallback else preferred_models
    
    # Find the first available model from our candidates
    model_name = None
    matched_prefix = None
    
    # First try exact matches
    for model in model_candidates:
        if model in available_models:
            model_name = model
            logger.info(f"Found exact match for model: {model_name}")
            break
    
    # If no exact match, try prefix matches
    if not model_name:
        for prefix in model_candidates:
            for available_model in available_models:
                if available_model.startswith(prefix):
                    model_name = available_model
                    matched_prefix = prefix
                    logger.info(f"Found prefix match for {prefix}: {model_name}")
                    break
            if model_name:
                break
    
    # If no preferred models are available, use any gemini model
    if not model_name and available_models:
        model_name = available_models[0]  # Use the first available model
        logger.info(f"No preferred models available, using: {model_name}")
    
    # Last resort fallback
    if not model_name:
        model_name = "gemini-1.0-pro"  # Default fallback if API didn't return models
        logger.warning(f"No models found in API response, using default: {model_name}")
    
    # Detailed logging about model selection
    logger.info(f"SELECTED MODEL: {model_name}")
    if matched_prefix:
        logger.info(f"Matched from prefix: {matched_prefix}")
    logger.info(f"Fallback mode: {use_fallback}")
    logger.info(f"Grounding enabled: {use_grounding}")
    logger.info(f"Tools configured: {len(tools)} tools")
    
    # Create the model instance
    model = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.0,  # Use zero temperature for deterministic function calling
        convert_system_message_to_human=False,  # Updated - no longer using deprecated approach
        tools=tools if tools else None,  # Pass the function definitions and grounding tools to the model
        max_retries=1,  # Reduce retry attempts to fail faster
        additional_kwargs={
            "tool_choice": "auto"  # Enable automatic tool choice for OpenAI compatibility
        }
    )
    
    logger.info(f"Successfully created LLM instance with model: {model_name}")
    return model

# System message to help the LLM understand available functions
def get_system_prompt():
    """Get the system prompt for the LLM with instructions about function usage"""
    return """You are a helpful AI assistant for an educational platform. 
You have access to tools that you can call to retrieve information or perform actions.

GUIDELINES FOR TOOL CALLING:
1. When a user asks for specific information that requires database access, like courses, FAQs, or user details, ALWAYS use the appropriate function tool.
2. Call functions with all required parameters and appropriate optional parameters when helpful.
3. Directly respond to simple questions that don't require database access.
4. Return function execution results in a user-friendly format.
5. If a function returns an error, explain the issue to the user in simple terms.
6. When multiple functions might apply, choose the most specific one for the task.

FUNCTION CALLING INSTRUCTIONS:
- ALWAYS use function calling for retrieving data from the system
- When function calling is needed, call the function FIRST, then provide your response
- DO NOT make up information about courses, users, assignments, or other system data
- DO format function arguments correctly based on the function's parameter schema
- Each function call will be automatically executed and the results will be returned to you

IMPORTANT: You MUST use the EXACT OpenAI function calling format when using tools.
The correct format is:
{
  "tool_calls": [
    {
      "id": "call_9g1881818181818181818181",
      "type": "function",
      "function": {
        "name": "function_name",
        "arguments": "{}"
      }
    }
  ]
}

For example, to call getCourses:
{
  "tool_calls": [
    {
      "id": "call_9g1881818181818181818181",
      "type": "function",
      "function": {
        "name": "getCourses",
        "arguments": "{}"
      }
    }
  ]
}

GROUNDING INSTRUCTIONS:
- When you need information that is not available in the system or might be outdated, use Google Search
- For questions about current events, latest technologies, or general knowledge not specific to the educational platform, use grounding
- Use grounding to complement the system data, especially for providing up-to-date information
- Properly attribute information obtained through grounding by mentioning the source

IMPORTANT EXAMPLES:
- If user asks "Show me my courses", call the getCourses() function using the EXACT format above
- If user asks "What are my assignments?", call the getAssignments() function
- If user asks "Find FAQs about enrollment", call the search_faqs(query="enrollment") function
- If user asks about something not related to the system, like "What are the latest trends in AI?", use Google Search for grounding

Be helpful, concise, and professional in all your responses."""

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
    
    # Check for various tool/function call formats
    
    # 1. Check for OpenAI format tool_calls
    if hasattr(response, 'additional_kwargs') and response.additional_kwargs.get('tool_calls'):
        logger.info("Found tool_calls in OpenAI format")
        tool_calls = response.additional_kwargs.get('tool_calls', [])
        
        for tool_call in tool_calls:
            # Handle OpenAI-style tool call
            if isinstance(tool_call, dict) and 'function' in tool_call:
                function_name = tool_call['function'].get('name')
                
                # Parse arguments
                if 'arguments' in tool_call['function']:
                    args_str = tool_call['function'].get('arguments', '{}')
                    # Convert from string if needed
                    if isinstance(args_str, str):
                        try:
                            args = json.loads(args_str)
                        except json.JSONDecodeError:
                            args = {}
                    else:
                        args = args_str
                        
                    function_calls.append({
                        "name": function_name,
                        "arguments": args
                    })
                    logger.info(f"Parsed OpenAI-format function call: {function_name}")
    
    # 2. Check for LangChain standard tool_calls attribute
    elif hasattr(response, 'tool_calls') and response.tool_calls:
        logger.info(f"Found tool_calls directly on response: {response.tool_calls}")
        
        for tool_call in response.tool_calls:
            # Skip Google Search grounding tool calls
            if tool_call.get("name") == "google_search":
                logger.info(f"Found Google Search grounding call: {tool_call}")
                continue
            
            function_calls.append({
                "name": tool_call.get("name"),
                "arguments": tool_call.get("args", {})
            })
            logger.info(f"Parsed LangChain tool call: {tool_call.get('name')}")
    
    # 3. Check legacy function_call format
    elif hasattr(response, 'additional_kwargs') and 'function_call' in response.additional_kwargs:
        function_call = response.additional_kwargs['function_call']
        function_name = function_call.get('name')
        args_str = function_call.get('arguments', '{}')
        
        try:
            if isinstance(args_str, str):
                args = json.loads(args_str)
            else:
                args = args_str
        except json.JSONDecodeError:
            logger.error(f"Failed to parse function arguments: {args_str}")
            args = {}
        
        function_calls.append({
            "name": function_name,
            "arguments": args
        })
        logger.info(f"Parsed legacy function call: {function_name}")
    
    # Add function calls to response if we found any
    if function_calls:
        if not hasattr(response, 'additional_kwargs'):
            response.additional_kwargs = {}
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
