import os
import logging
import json
import time
import requests
import re  # Add import at the top level
from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.services.function_router import function_router
import asyncio
import aiohttp
import backoff
from app.models.user import User
from app.config import settings

logger = logging.getLogger(__name__)

# Available models cache to avoid repeated API calls
_available_models_cache = None

# Gemini API configuration
GEMINI_API_KEY = settings.GOOGLE_API_KEY
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
GEMINI_MODEL = "gemini-2.5-pro-exp"

INSIGHT_PROMPT_TEMPLATE = """
You are an AI learning analytics expert integrated into an educational platform. Your task is to analyze a student's learning data and provide personalized insights to help improve their learning outcomes.

## User Information
- Name: {name}
- Email: {email}

## Learning Data (JSON format)
```json
{data}
```

## Instructions
Analyze the provided learning data to generate personalized insights. Focus on:
1. Study patterns (when and how they learn best)
2. Content preferences
3. Strengths and weaknesses
4. Specific improvement recommendations
5. Learning opportunities tailored to their needs

## Response Format
Return a JSON object with the following structure:
```json
{
  "studyPatterns": {
    "optimalTime": "String describing when they learn best",
    "preferredContent": "String describing content they engage with most",
    "recommendedSchedule": "String with specific time suggestions"
  },
  "suggestions": {
    "contentType": "String with recommended content type to focus on",
    "reason": "String explaining why this content type is recommended",
    "topic": "String with a specific topic to focus on (if applicable)"
  },
  "opportunities": [
    {
      "type": "String (quiz, review, practice, etc.)",
      "subject": "String with specific subject",
      "reason": "String explaining why this opportunity is valuable"
    },
    {
      "type": "String (quiz, review, practice, etc.)",
      "subject": "String with specific subject",
      "reason": "String explaining why this opportunity is valuable"
    }
  ],
  "statistics": {
    "completionRate": Number,
    "quizAverage": Number,
    "activeLastMonth": Number,
    "strengthTopics": [String topics they excel at]
  }
}
```

Important guidelines:
- Make insights actionable, specific, and personalized
- Base all insights on the actual data provided
- Use a professional, encouraging tone
- Do not reference your own capabilities or that you are an AI
- Focus only on providing the JSON output without any other text

"""

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
def get_llm(functions=None, use_fallback=False, use_grounding=True, force_tool_choice=False):
    """Get the LLM model instance with function calling enabled
    
    Args:
        functions: List of function declarations to pass to the model
        use_fallback: Whether to use the fallback model (gemini-2.0-flash)
        use_grounding: Whether to enable grounding capabilities
        force_tool_choice: Force the model to use tool calling (for testing)
        
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
        tools.append({"type": "google_search"})
    
    # Get available models
    available_models = get_available_models()
    logger.info(f"All available models: {available_models}")
    
    # Define model preferences - updated with newest experimental models first
    preferred_models = [
        # Use Gemini 2.5 preview first
        "gemini-2.5-pro-preview",
        "gemini-2.5-pro-exp",
        
        # Then Gemini 2.0 flash
        "gemini-2.0-flash",
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash-exp-image-generation",
        
        # Other experimental versions
        "gemini-exp-",
        "gemini-2.0-pro-exp",
        
        # Fallback to other models
        "gemini-1.5-pro-latest",
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
    
    # Clean up model names for matching (strip 'models/' prefix)
    clean_available_models = [m.replace('models/', '') if m.startswith('models/') else m for m in available_models]
    logger.debug(f"Clean available models: {clean_available_models}")
    
    # First try exact matches (with more flexible name handling)
    for model in model_candidates:
        # Check for exact match
        if model in clean_available_models:
            model_name = model
            logger.info(f"Found exact match for model: {model_name}")
            break
            
        # Also check for model names that contain our candidate (for versioned models like gemini-2.5-pro-preview-03-25)
        matching_models = [m for m in clean_available_models if model in m]
        if matching_models:
            model_name = matching_models[0]  # Use the first match
            logger.info(f"Found match for {model}: {model_name}")
            break
    
    # If no exact match, try prefix matches
    if not model_name:
        for prefix in model_candidates:
            matching_models = [m for m in clean_available_models if m.startswith(prefix)]
            if matching_models:
                model_name = matching_models[0]  # Use the first match
                matched_prefix = prefix
                logger.info(f"Found prefix match for {prefix}: {model_name}")
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
    
    # Set tool_choice parameter based on whether we're forcing tool calling
    tool_choice = None
    if force_tool_choice and tools and len(tools) > 0:
        # Force using the first available tool
        first_tool = tools[0]
        if isinstance(first_tool, dict) and "function" in first_tool:
            tool_name = first_tool["function"].get("name")
            logger.info(f"Forcing tool choice to: {tool_name}")
            tool_choice = {"type": "function", "function": {"name": tool_name}}
        else:
            # Default to "auto" if we can't extract the tool name
            tool_choice = "auto"
    else:
        # Use automatic tool choice by default
        tool_choice = "auto"
    
    # Create the model instance
    model = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.0,  # Use zero temperature for deterministic function calling
        convert_system_message_to_human=False,  # Updated - no longer using deprecated approach
        tools=tools if tools else None,  # Pass the function definitions and grounding tools to the model
        max_retries=1,  # Reduce retry attempts to fail faster
        additional_kwargs={
            "tool_choice": tool_choice  # Use the configured tool choice
        }
    )
    
    logger.info(f"Successfully created LLM instance with model: {model_name}")
    return model

# System message to help the LLM understand available functions
def get_system_prompt():
    """Get the system prompt for the LLM with instructions about function usage"""
    return """
    You are a helpful AI assistant for an educational platform. 
You have access to tools that you can call to retrieve information or perform actions.
You should answer only about course-related questions.
For quiz and assignment-related questions, avoid direct answers and guide the user to the correct answer by providing step-by-step help.
Talk only about courses and don't talk about other topics.

CRITICAL INSTRUCTIONS ABOUT FUNCTIONS:
1. When a user asks for specific information that requires database access, like courses, FAQs, or user details, you MUST use the appropriate function tool.
2. DO NOT ATTEMPT TO ANSWER DATABASE QUERIES DIRECTLY - you MUST call a function to get the data.
3. Always return function calls in the EXACT FORMAT expected by the API.
4. NEVER use natural language to describe a function call - only use the proper format.

FUNCTION CALLING FORMAT:
You must use this EXACT format when calling a function:
{
  "type": "function",
  "function": {
    "name": "functionName",
    "arguments": {
      "param1": "value1",
      "param2": 42
    }
  }
}

DO NOT use other formats like:
- functionName(param1="value1", param2=42)
- print(functionName(...))
- Direct function printing in markdown code blocks

WHEN TO USE FUNCTIONS:
- When the user asks about their courses, use getCourses
- When the user asks about their profile, use getUserProfile
- When the user asks about assignments for a course, use getAssignments
- When the user asks a question about the platform, use search_faqs
- When the user needs general knowledge not in our system, use web_search

EXAMPLES OF CORRECT FUNCTION CALLS:
If user asks "What courses am I taking?", respond only with:
{
  "type": "function",
  "function": {
    "name": "getCourses",
    "arguments": {
      "user_id": "current_user"
    }
  }
}

If user asks about assignments in a course, respond only with:
{
  "type": "function",
  "function": {
    "name": "getAssignments",
    "arguments": {
      "course_id": "course123"
    }
  }
}

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
        
        # Add detailed debugging info before calling the model
        logger.debug(f"Function declarations used: {len(formatted_functions)}")
        for idx, func in enumerate(formatted_functions[:5]):  # Log first 5 functions
            logger.debug(f"Function {idx}: {func.get('function', {}).get('name')} - {func.get('type')}")
        
        # Print the first message to help with debugging
        if prompt and len(prompt) > 0:
            logger.debug(f"First prompt message type: {type(prompt[0]).__name__}")
            if hasattr(prompt[0], 'content'):
                logger.debug(f"First message content excerpt: {prompt[0].content[:200]}...")
        
        # Make the actual call to the LLM
        response = await llm.ainvoke(prompt)
        elapsed = time.time() - start_time
        logger.info(f"LLM response received in {elapsed:.2f} seconds")
        
        # Enhanced detailed logging of the response
        logger.debug(f"Response type: {type(response).__name__}")
        logger.debug(f"Response attributes: {dir(response)}")
        
        # Log the raw response for debugging
        if hasattr(response, 'additional_kwargs'):
            logger.debug(f"Response additional_kwargs keys: {list(response.additional_kwargs.keys())}")
            logger.debug(f"Response additional_kwargs content: {json.dumps(response.additional_kwargs, default=str)}")
        
        if hasattr(response, 'content'):
            content_preview = response.content[:500] + ('...' if len(response.content) > 500 else '') if response.content else 'None'
            logger.debug(f"Response content preview: {content_preview}")
            
        # Check for standard tool_calls attribute directly on AIMessage from LangChain
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.debug(f"Direct tool_calls attribute found: {json.dumps(response.tool_calls, default=str)}")

        # Check for grounding evidence in the response
        has_grounding = False
        if hasattr(response, 'additional_kwargs') and 'grounding' in str(response.additional_kwargs):
            has_grounding = True
            logger.info("Grounding information detected in response")
        
        # Process tool/function calls from the response
        function_calls = []
        
        try:
            # Check for tool_calls in the LangChain response object
            if hasattr(response, 'additional_kwargs') and 'tool_calls' in response.additional_kwargs:
                logger.info("Found tool_calls in response additional_kwargs")
                tool_calls = response.additional_kwargs['tool_calls']
                
                for tool_call in tool_calls:
                    if isinstance(tool_call, dict) and 'function' in tool_call:
                        func_info = tool_call['function']
                        if 'name' in func_info:
                            func_name = func_info['name']
                            
                            # Parse arguments
                            args = {}
                            if 'arguments' in func_info:
                                args_str = func_info['arguments']
                                if isinstance(args_str, str):
                                    try:
                                        args = json.loads(args_str)
                                    except json.JSONDecodeError:
                                        logger.error(f"Failed to parse arguments for {func_name}: {args_str}")
                                        args = {}
                                else:
                                    args = args_str
                            
                            function_calls.append({
                                "name": func_name,
                                "arguments": args
                            })
                            logger.info(f"Parsed function call: {func_name} with args: {args}")
                        
            # Also check LangChain's direct tool_calls attribute 
            elif hasattr(response, 'tool_calls') and response.tool_calls:
                logger.info("Found tool_calls attribute on the response object")
                for tool_call in response.tool_calls:
                    # Skip grounding calls
                    if 'name' in tool_call and tool_call['name'] == 'google_search':
                        continue
                        
                    func_name = tool_call.get('name')
                    func_args = tool_call.get('args', {})
                    
                    function_calls.append({
                        "name": func_name,
                        "arguments": func_args
                    })
                    logger.info(f"Parsed tool call: {func_name} with args: {func_args}")
                    
            # Check legacy function_call format as fallback
            elif hasattr(response, 'additional_kwargs') and 'function_call' in response.additional_kwargs:
                logger.info("Found legacy function_call format")
                func_call = response.additional_kwargs['function_call']
                if isinstance(func_call, dict) and 'name' in func_call:
                    func_name = func_call['name']
                    
                    # Parse arguments
                    args = {}
                    if 'arguments' in func_call:
                        args_str = func_call['arguments']
                        if isinstance(args_str, str):
                            try:
                                args = json.loads(args_str)
                            except json.JSONDecodeError:
                                logger.error(f"Failed to parse arguments for {func_name}: {args_str}")
                                args = {}
                        else:
                            args = args_str
                            
                    function_calls.append({
                        "name": func_name,
                        "arguments": args
                    })
                    logger.info(f"Parsed legacy function call: {func_name} with args: {args}")
            
            # NEW: Check content for structured tool calls (some models embed them in content)
            if not function_calls and hasattr(response, 'content') and response.content:
                content = response.content
                logger.info("Checking content for embedded function calls")
                
                # Try to extract function calls from content using regex pattern matching
                if isinstance(content, str):
                    # Pattern 1: Look for JSON-like function call structures
                    try:
                        import re
                        # Match patterns like: {"type":"function","function":{"name":"func_name","arguments":{...}}}
                        pattern = r'\{\s*"type"\s*:\s*"function"\s*,\s*"function"\s*:\s*\{[^}]*"name"\s*:\s*"([^"]+)"[^}]*"arguments"\s*:\s*(\{[^}]+\})'
                        matches = re.findall(pattern, content)
                        
                        for match in matches:
                            func_name = match[0]
                            try:
                                args = json.loads(match[1])
                                function_calls.append({
                                    "name": func_name,
                                    "arguments": args
                                })
                                logger.info(f"Extracted embedded function call from content: {func_name}")
                            except json.JSONDecodeError:
                                logger.error(f"Failed to parse arguments for embedded function call: {match[1]}")
                        
                        # If still no matches, try looser pattern
                        if not function_calls:
                            # Look for function call annotations using markdown or similar
                            func_pattern = r'function(?:_call|Call)?\s*:\s*([a-zA-Z0-9_]+)'
                            arg_pattern = r'arguments\s*:\s*(\{[^}]+\})'
                            
                            func_matches = re.findall(func_pattern, content)
                            arg_matches = re.findall(arg_pattern, content)
                            
                            if func_matches and arg_matches and len(func_matches) == len(arg_matches):
                                for i in range(len(func_matches)):
                                    try:
                                        args = json.loads(arg_matches[i])
                                        function_calls.append({
                                            "name": func_matches[i],
                                            "arguments": args
                                        })
                                        logger.info(f"Extracted loose function call from content: {func_matches[i]}")
                                    except json.JSONDecodeError:
                                        logger.error(f"Failed to parse arguments for loose function call: {arg_matches[i]}")
                    except Exception as e:
                        logger.error(f"Error extracting function calls from content: {str(e)}")
                            
        except Exception as e:
            logger.error(f"Error parsing function calls: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Add extracted function calls to the response
        if function_calls:
            logger.info(f"Adding {len(function_calls)} function calls to response")
            if not hasattr(response, 'additional_kwargs'):
                response.additional_kwargs = {}
            response.additional_kwargs['function_calls'] = function_calls
        
        # Ensure there is always some content in the response
        if not response.content or response.content.strip() == '':
            # If we have function calls but no content, add a more informative message
            if function_calls:
                response.content = "I'm processing your request through our system..."
            else:
                # If no function calls and no content, provide a more helpful response
                response.content = "I apologize, but I couldn't generate a proper response. Please try rephrasing your question or providing more details."
                logger.info("Added more helpful fallback content to empty response")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in primary model: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Try fallback model if enabled
        if not use_fallback:
            logger.info("Attempting fallback model...")
            return await call_llm(messages, use_fallback=True, use_grounding=use_grounding)
        else:
            raise

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

@backoff.on_exception(
    backoff.expo,
    (aiohttp.ClientError, asyncio.TimeoutError),
    max_tries=3,
    max_time=30
)
async def generate_learning_insights(user: User, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Generate enhanced learning insights using the Gemini API
    
    Args:
        user: User object
        data: Dictionary containing user learning analytics data
        
    Returns:
        Dict containing AI-generated learning insights or None if generation fails
    """
    if not GEMINI_API_KEY:
        logger.warning("Gemini API key not configured, skipping enhanced insights generation")
        return None
    
    try:
        # Format the prompt with user data
        prompt = INSIGHT_PROMPT_TEMPLATE.format(
            name=user.name or "Student",
            email=user.email,
            data=json.dumps(data, default=str)
        )
        
        # Create request payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "topK": 40,
                "maxOutputTokens": 2048,
                "responseMimeType": "application/json"
            }
        }
        
        # Send request to Gemini API
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }
        
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                # Check for successful response
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Gemini API error: {response.status}, {error_text}")
                    return None
                
                # Parse the response
                response_data = await response.json()
                
                # Extract the content from the response
                if "candidates" in response_data and response_data["candidates"]:
                    candidate = response_data["candidates"][0]
                    if "content" in candidate and candidate["content"]["parts"]:
                        # Extract the JSON text from the response
                        result_text = candidate["content"]["parts"][0]["text"]
                        
                        # Try to parse the JSON (clean it if necessary)
                        try:
                            # Clean up the text to extract just the JSON part
                            json_text = result_text.strip()
                            if json_text.startswith("```json"):
                                json_text = json_text.split("```json", 1)[1]
                            if "```" in json_text:
                                json_text = json_text.split("```", 1)[0]
                            
                            json_text = json_text.strip()
                            insights = json.loads(json_text)
                            
                            # Validate the response format
                            if not all(key in insights for key in ["studyPatterns", "suggestions", "opportunities"]):
                                logger.warning("Gemini response missing required fields")
                                return None
                            
                            logger.info(f"Successfully generated enhanced learning insights for user {user.id}")
                            return insights
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse JSON from Gemini response: {e}")
                            logger.debug(f"Raw response text: {result_text}")
                            return None
                
                logger.warning("Unexpected Gemini API response format")
                return None
                
    except Exception as e:
        logger.error(f"Error generating insights with Gemini: {str(e)}")
        return None

# Additional LLM utility functions can be added here
async def summarize_lecture_text(text: str, max_length: int = 1000) -> Optional[str]:
    """
    Summarize lecture text using Gemini API (placeholder for implementation)
    """
    # Implementation would be similar to generate_learning_insights but with different prompt
    pass

async def generate_quiz_questions(topic: str, difficulty: str, count: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    Generate quiz questions for a given topic using Gemini API (placeholder for implementation)
    """
    # Implementation would be similar to generate_learning_insights but with different prompt
    pass

# Add diagnostic function at the end of the file
async def debug_function_calling(test_query="What courses am I enrolled in?"):
    """Test function calling with a simple example"""
    logger.info(f"Running function calling diagnostic test with query: {test_query}")
    
    test_messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": test_query}
    ]
    
    # Create a simple test function declaration
    test_functions = [{
        "name": "getCourses",
        "description": "Get courses for a user",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User ID"}
            },
            "required": ["user_id"]
        }
    }]
    
    # Format the function for the model
    formatted_functions = [{
        "type": "function",
        "function": {
            "name": func["name"],
            "description": func["description"],
            "parameters": func["parameters"]
        }
    } for func in test_functions]
    
    # Test with forcing function calling
    try:
        # Try multiple models to find one that works with function calling
        test_models = [
            "gemini-1.5-pro", 
            "gemini-1.5-flash",
            "gemini-1.0-pro"
        ]
        
        results = {}
        
        # Test without forcing tool choice first
        for model_name in test_models:
            logger.info(f"Testing function calling with model (auto tool choice): {model_name}")
            
            # Create test model with automatic tool choice
            model = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0,
                tools=formatted_functions,
                max_retries=1,
                additional_kwargs={"tool_choice": "auto"}
            )
            
            # Make the call
            try:
                response = await model.ainvoke(test_messages)
                
                logger.info(f"Model {model_name} response received")
                logger.info(f"Response content: {response.content}")
                
                has_tool_calls = False
                tool_calls_info = "None"
                
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    has_tool_calls = True
                    tool_calls_info = str(response.tool_calls)
                    
                if hasattr(response, 'additional_kwargs') and 'tool_calls' in response.additional_kwargs:
                    has_tool_calls = True
                    tool_calls_info = str(response.additional_kwargs['tool_calls'])
                
                results[model_name] = {
                    "success": has_tool_calls,
                    "tool_calls": tool_calls_info,
                    "content": response.content
                }
                
                # If we found a working model, update the preferred models list
                if has_tool_calls:
                    logger.info(f"Model {model_name} successfully generated function calls")
                    break
                    
            except Exception as e:
                logger.error(f"Error testing model {model_name}: {str(e)}")
                results[model_name] = {"error": str(e)}
        
        # Now test with forced tool choice
        logger.info("Testing with forced tool choice...")
        for model_name in test_models:
            logger.info(f"Testing function calling with model (forced tool choice): {model_name}")
            
            # Force the model to call our test function
            forced_tool_choice = {
                "type": "function", 
                "function": {"name": "getCourses"}
            }
            
            # Create test model with forced tool choice
            model = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0,
                tools=formatted_functions,
                max_retries=1,
                additional_kwargs={"tool_choice": forced_tool_choice}
            )
            
            # Make the call
            try:
                response = await model.ainvoke(test_messages)
                
                logger.info(f"Model {model_name} (forced tool) response received")
                logger.info(f"Response content: {response.content}")
                
                has_tool_calls = False
                tool_calls_info = "None"
                
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    has_tool_calls = True
                    tool_calls_info = str(response.tool_calls)
                    
                if hasattr(response, 'additional_kwargs') and 'tool_calls' in response.additional_kwargs:
                    has_tool_calls = True
                    tool_calls_info = str(response.additional_kwargs['tool_calls'])
                
                results[f"{model_name}_forced"] = {
                    "success": has_tool_calls,
                    "tool_calls": tool_calls_info,
                    "content": response.content
                }
                
                # If we found a working model, note it
                if has_tool_calls:
                    logger.info(f"Model {model_name} with forced tool choice successfully generated function calls")
                    # Note this model works with forced tool choice for future reference
                    results["working_model_forced"] = model_name
                    break
                    
            except Exception as e:
                logger.error(f"Error testing model {model_name} with forced tool: {str(e)}")
                results[f"{model_name}_forced"] = {"error": str(e)}
        
        return results
        
    except Exception as e:
        logger.error(f"Diagnostic test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e)}
