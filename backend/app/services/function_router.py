from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel
from fastapi import HTTPException
import inspect
import json
from functools import wraps
import logging

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

    async def execute_function(self, name: str, args: Dict[str, Any], user_role: Optional[str] = None) -> Any:
        """
        Execute a registered function with given arguments
        
        Args:
            name: Function name to execute
            args: Arguments to pass to the function
            user_role: Optional role of the user executing the function
            
        Returns:
            Function execution result
            
        Raises:
            HTTPException: If function not found, user doesn't have permission, or execution fails
        """
        logger.info(f"Executing function: {name} with user_role: {user_role}")
        
        if name not in self._functions:
            logger.warning(f"Function {name} not found")
            raise HTTPException(status_code=404, detail=f"Function {name} not found")
        
        # Check role-based access
        function_info = self._functions[name]
        declaration = function_info.get("declaration", {})
        
        if user_role and "roles" in declaration and declaration.get("roles"):
            allowed_roles = declaration.get("roles", [])
            if user_role.lower() not in [r.lower() for r in allowed_roles] and user_role.lower() != "admin":
                logger.warning(f"User with role '{user_role}' not authorized to execute function '{name}'")
                raise HTTPException(
                    status_code=403, 
                    detail=f"User with role '{user_role}' is not authorized to execute function '{name}'"
                )
        
        try:
            handler = function_info.get("handler")
            if not handler:
                logger.error(f"No handler found for function {name}")
                raise HTTPException(status_code=500, detail=f"Function {name} has no handler")
            
            if inspect.iscoroutinefunction(handler):
                logger.debug(f"Executing async function {name}")
                return await handler(**args)
            
            logger.debug(f"Executing sync function {name}")
            return handler(**args)
        except Exception as e:
            logger.error(f"Error executing function {name}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error executing function {name}: {str(e)}")

    def function_declaration(self, name: str, description: str, parameters: Dict[str, Any], roles: Optional[List[str]] = None):
        """
        Decorator to register API endpoint functions
        
        Example:
            @function_router.function_declaration(
                name="get_courses",
                description="Get available courses",
                parameters={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Course category"
                        }
                    }
                },
                roles=["student", "faculty", "admin"]
            )
            async def get_courses(category: str):
                # Function implementation
                pass
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            
            self.register_function(name, description, wrapper, parameters, roles)
            return wrapper
        return decorator

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

# Create global function router instance
function_router = FunctionRouter() 