from typing import List, Dict, Any, Optional, Set, Tuple
from pydantic import BaseModel
from fastapi import HTTPException
import inspect
import json
from functools import wraps
import logging
import asyncio
import re

logger = logging.getLogger(__name__)

class FunctionDeclaration(BaseModel):
    """Schema for function declarations that Gemini can understand"""
    name: str
    description: str
    parameters: Dict[str, Any]
    roles: Optional[List[str]] = None  # List of roles that can access this function

class FunctionRouter:
    """
    Function router service that manages available functions and their declarations
    for Gemini to use in compositional function calling.
    """
    def __init__(self):
        self._functions: Dict[str, Dict] = {}
        self._function_declarations: List[Dict] = []
        self._function_registry: Dict[str, Dict] = {}

    def register_function(self, name: str, description: str, handler, parameters: Dict[str, Any], roles: Optional[List[str]] = None):
        """
        Register a new function with its declaration and handler
        
        Args:
            name: Function name
            description: Function description
            handler: The actual function to be called
            parameters: OpenAPI compatible parameter schema
            roles: Optional list of roles that can access this function (None means all roles)
        """
        try:
            if not name or not isinstance(name, str):
                logger.error(f"Invalid function name: {name}")
                return
            
            if not handler or not callable(handler):
                logger.error(f"Invalid handler for function {name}")
                return
            
            logger.info(f"Registering function: {name}, roles: {roles}")
            
            # Ensure parameters is a dictionary
            if not parameters:
                parameters = {"type": "object", "properties": {}}
            
            # Ensure roles is a list or None
            if roles and not isinstance(roles, list):
                roles = [str(roles)]
            
            self._functions[name] = {
                "handler": handler,
                "declaration": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                    "roles": roles
                }
            }
            self._function_declarations.append(self._functions[name]["declaration"])
            logger.debug(f"Function {name} registered successfully")
        except Exception as e:
            logger.error(f"Error registering function {name}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

    def get_function_declarations(self, role: Optional[str] = None) -> List[Dict]:
        """
        Get registered function declarations for Gemini, optionally filtered by role
        
        Args:
            role: Optional role to filter functions by
            
        Returns:
            List of function declarations accessible to the given role
        """
        try:
            # If no role specified or role is "admin", return all functions
            if role is None or role.lower() == "admin":
                logger.debug(f"Returning all {len(self._function_declarations)} functions for admin/unspecified role")
                return self._function_declarations
            
            # Filter functions based on role
            filtered_functions = [
                func for func in self._function_declarations
                if "roles" not in func or func.get("roles") is None or role.lower() in [r.lower() for r in func.get("roles", [])]
            ]
            
            logger.debug(f"Filtered functions by role '{role}': {len(filtered_functions)} of {len(self._function_declarations)}")
            return filtered_functions
        except Exception as e:
            logger.error(f"Error in get_function_declarations: {str(e)}")
            # Return empty list in case of error to avoid breaking the application
            return []

    def get_canonical_function_name(self, name: str) -> Optional[str]:
        """
        Get the canonical function name, handling different case conventions
        
        For example, if 'getCourses' and 'get_courses' are both registered,
        this method will return the registered name for either input.
        
        Args:
            name: The function name to check
            
        Returns:
            The canonical function name if it exists, or None
        """
        # Check direct match first
        if name in self._functions:
            return name
            
        # Try to match camelCase to snake_case and vice versa
        snake_case = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        if snake_case in self._functions:
            logger.info(f"Matched function {name} to canonical name {snake_case}")
            return snake_case
            
        # Convert snake_case to camelCase
        camel_case_parts = name.split('_')
        camel_case = camel_case_parts[0] + ''.join(x.title() for x in camel_case_parts[1:])
        if camel_case in self._functions:
            logger.info(f"Matched function {name} to canonical name {camel_case}")
            return camel_case
            
        # No match found
        return None

    async def execute_function(self, name: str, arguments: Dict[str, Any], role: Optional[str] = None) -> Any:
        """
        Execute a registered function with the given arguments
        
        Args:
            name: Name of the function to execute
            arguments: Arguments to pass to the function
            role: Optional role to check permissions against
            
        Returns:
            Function result
            
        Raises:
            HTTPException: If function execution fails
        """
        # Check function exists
        if name not in self._functions:
            raise HTTPException(status_code=404, detail=f"Function {name} not found")
            
        # Check role permissions
        func_info = self._functions[name]
        if role and func_info["roles"] and role not in func_info["roles"]:
            raise HTTPException(status_code=403, detail=f"Role {role} not authorized for function {name}")
            
        # Validate arguments
        is_valid, error = self.validate_function_call(name, arguments)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
            
        try:
            # Execute function
            result = await func_info["handler"](**arguments)
            
            # Format response
            if result is None:
                return {"status": "success"}
            elif isinstance(result, (str, int, float, bool)):
                return {"result": result}
            elif isinstance(result, (list, dict)):
                return result
            else:
                return {"result": str(result)}
                
        except Exception as e:
            # Log error
            import traceback
            traceback.print_exc()
            
            # Return error response
            raise HTTPException(
                status_code=500,
                detail=f"Function execution failed: {str(e)}"
            )

    def function_declaration(self, name: str, description: str, parameters: Dict[str, Any], roles: Optional[List[str]] = None):
        """
        Decorator for registering functions with the router
        
        Args:
            name: Name of the function
            description: Description of what the function does
            parameters: JSON schema of the function parameters
            roles: Optional list of roles allowed to execute this function
        """
        def decorator(func):
            # Validate and normalize the parameter schema
            schema = {
                "type": "object",
                "properties": parameters.get("properties", {}),
                "required": parameters.get("required", []),
                "additionalProperties": parameters.get("additionalProperties", True)
            }
            
            # Add type information if missing
            for prop_name, prop_info in schema["properties"].items():
                if "type" not in prop_info:
                    # Try to infer type from any default value
                    if "default" in prop_info:
                        default_type = type(prop_info["default"]).__name__
                        prop_info["type"] = {
                            "str": "string",
                            "int": "integer",
                            "float": "number",
                            "bool": "boolean",
                            "list": "array",
                            "dict": "object"
                        }.get(default_type, "string")
                    else:
                        # Default to string if no type info available
                        prop_info["type"] = "string"
            
            # Create the function declaration
            declaration = {
                "name": name,
                "description": description,
                "parameters": schema
            }
            
            if roles:
                declaration["roles"] = roles
            
            # Register the function
            self._functions[name] = {
                "handler": func,
                "declaration": declaration,
                "roles": roles
            }
            
            # Add function to the registry for schema generation
            self._function_registry[name] = {
                "function": func,
                "parameters": schema,
                "description": description
            }
            
            logger.info(f"Registered function {name} with schema: {schema}")
            return func
            
        return decorator

    def get_function_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """Get the schema for a specific function"""
        if name in self._functions:
            return self._functions[name]["declaration"]["parameters"]
        return None

    async def web_search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Perform a web search for the given query.
        
        Args:
            query: The search query
            num_results: Maximum number of results to return
            
        Returns:
            List of search results with title, snippet, and url
        """
        try:
            # This is a mock implementation - in production, you would integrate with a real search API
            # such as Google Custom Search, Bing Search, or similar
            logger.info(f"Performing web search for: {query}")
            
            # Mock results - in a real implementation, this would call an external API
            mock_results = [
                {
                    "title": "Understanding Function Calling in LLMs",
                    "snippet": "Function calling allows LLMs to interact with external tools while still using their reasoning capabilities.",
                    "url": "https://example.com/function-calling-llm"
                },
                {
                    "title": "Gemini API Documentation",
                    "snippet": "Gemini can use both its knowledge and function calling to provide comprehensive responses.",
                    "url": "https://ai.google.dev/docs/gemini_api"
                },
                {
                    "title": "Best Practices for AI Assistants",
                    "snippet": "Effective AI assistants combine model knowledge with external tools for the best user experience.",
                    "url": "https://example.com/ai-assistant-best-practices"
                }
            ]
            
            # Return limited number of results
            return mock_results[:num_results]
        except Exception as e:
            logger.error(f"Error in web_search: {str(e)}")
            return [{"title": "Error", "snippet": f"Failed to perform web search: {str(e)}", "url": ""}]

    def validate_function_call(self, name: str, arguments: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a function call before execution
        
        Args:
            name: Name of the function to validate
            arguments: Arguments to validate against the function schema
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if name not in self._functions:
            return False, f"Function {name} not found"
            
        schema = self._functions[name]["declaration"]["parameters"]
        
        # Check required parameters
        for required in schema.get("required", []):
            if required not in arguments:
                return False, f"Missing required parameter: {required}"
        
        # Validate parameter types
        for param_name, param_value in arguments.items():
            if param_name not in schema["properties"]:
                if not schema.get("additionalProperties", True):
                    return False, f"Unknown parameter: {param_name}"
                continue
                
            param_schema = schema["properties"][param_name]
            param_type = param_schema["type"]
            
            # Type validation
            if param_type == "string" and not isinstance(param_value, str):
                return False, f"Parameter {param_name} must be a string"
            elif param_type == "number" and not isinstance(param_value, (int, float)):
                return False, f"Parameter {param_name} must be a number"
            elif param_type == "integer" and not isinstance(param_value, int):
                return False, f"Parameter {param_name} must be an integer"
            elif param_type == "boolean" and not isinstance(param_value, bool):
                return False, f"Parameter {param_name} must be a boolean"
            elif param_type == "array" and not isinstance(param_value, list):
                return False, f"Parameter {param_name} must be an array"
            elif param_type == "object" and not isinstance(param_value, dict):
                return False, f"Parameter {param_name} must be an object"
                
        return True, None

    def get_function_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a registered function
        
        Args:
            name: Name of the function
            
        Returns:
            Dictionary with function information or None if not found
        """
        if name not in self._functions:
            return None
            
        info = self._functions[name]
        return {
            "name": name,
            "description": info["declaration"]["description"],
            "parameters": info["declaration"]["parameters"],
            "roles": info["roles"],
            "handler": info["handler"]
        }

    def list_functions(self, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available functions, optionally filtered by role
        
        Args:
            role: Optional role to filter functions by
            
        Returns:
            List of function declarations
        """
        functions = []
        for name, info in self._functions.items():
            if role and info["roles"] and role not in info["roles"]:
                continue
                
            functions.append({
                "name": name,
                "description": info["declaration"]["description"],
                "parameters": info["declaration"]["parameters"],
                "roles": info["roles"]
            })
        return functions

# Create global function router instance
function_router = FunctionRouter() 

# Register API functions
from app.services.api_functions import (
    getUserProfile, getCourses, getAssignments, search_faqs,
    web_search, generate_learning_roadmap, get_course_with_grades
)

# Setup the router with all available functions
def setup_function_router():
    """Register all API functions with the router"""
    
    # User functions
    function_router.register_function(
        name="getUserProfile",
        description="Get a user's profile information",
        handler=getUserProfile,
        parameters={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID to get profile for"
                }
            },
            "required": ["user_id"]
        }
    )
    
    # Course functions
    function_router.register_function(
        name="getCourses",
        description="Get courses for a user with optional status filter",
        handler=getCourses,
        parameters={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID to get courses for"
                },
                "status": {
                    "type": "string",
                    "description": "Optional status filter (active, completed, etc.)"
                }
            },
            "required": ["user_id"]
        }
    )
    
    function_router.register_function(
        name="get_course_with_grades",
        description="Get a course with all student grades",
        handler=get_course_with_grades,
        parameters={
            "type": "object",
            "properties": {
                "course_id": {
                    "type": "string",
                    "description": "Course ID to get grades for"
                }
            },
            "required": ["course_id"]
        }
    )
    
    # Assignment functions
    function_router.register_function(
        name="getAssignments",
        description="Get assignments for a course with optional user filter",
        handler=getAssignments,
        parameters={
            "type": "object",
            "properties": {
                "course_id": {
                    "type": "string",
                    "description": "Course ID to get assignments for"
                },
                "user_id": {
                    "type": "string",
                    "description": "Optional user ID for filtering submissions"
                }
            },
            "required": ["course_id"]
        }
    )
    
    # FAQ functions
    function_router.register_function(
        name="search_faqs",
        description="Search FAQs based on query text and optional category",
        handler=search_faqs,
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query text"
                },
                "category": {
                    "type": "string",
                    "description": "Optional category filter"
                }
            },
            "required": ["query"]
        }
    )
    
    # Web search functions
    function_router.register_function(
        name="web_search",
        description="Search the web for information using the provided query",
        handler=web_search,
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    )
    
    # Learning roadmap functions
    function_router.register_function(
        name="generate_learning_roadmap",
        description="Generate a learning roadmap for a given topic and difficulty level",
        handler=generate_learning_roadmap,
        parameters={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic to create a roadmap for"
                },
                "difficulty": {
                    "type": "string",
                    "description": "Difficulty level (beginner, intermediate, advanced)",
                    "default": "beginner"
                }
            },
            "required": ["topic"]
        }
    )
    
    logger.info("Function router initialized with API functions")

# Initialize functions when module is imported
setup_function_router() 