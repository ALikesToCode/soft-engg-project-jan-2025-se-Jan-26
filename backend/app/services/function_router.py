from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import HTTPException
import inspect
import json
from functools import wraps

class FunctionDeclaration(BaseModel):
    """Schema for function declarations that Gemini can understand"""
    name: str
    description: str
    parameters: Dict[str, Any]

class FunctionRouter:
    """
    Function router service that manages available functions and their declarations
    for Gemini to use in compositional function calling.
    """
    def __init__(self):
        self._functions: Dict[str, Dict] = {}
        self._function_declarations: List[Dict] = []

    def register_function(self, name: str, description: str, handler, parameters: Dict[str, Any]):
        """
        Register a new function with its declaration and handler
        
        Args:
            name: Function name
            description: Function description
            handler: The actual function to be called
            parameters: OpenAPI compatible parameter schema
        """
        self._functions[name] = {
            "handler": handler,
            "declaration": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        self._function_declarations.append(self._functions[name]["declaration"])

    def get_function_declarations(self) -> List[Dict]:
        """Get all registered function declarations for Gemini"""
        return self._function_declarations

    async def execute_function(self, name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a registered function with given arguments
        
        Args:
            name: Function name to execute
            args: Arguments to pass to the function
            
        Returns:
            Function execution result
            
        Raises:
            HTTPException: If function not found or execution fails
        """
        if name not in self._functions:
            raise HTTPException(status_code=404, detail=f"Function {name} not found")
        
        try:
            handler = self._functions[name]["handler"]
            if inspect.iscoroutinefunction(handler):
                return await handler(**args)
            return handler(**args)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error executing function {name}: {str(e)}")

    def function_declaration(self, name: str, description: str, parameters: Dict[str, Any]):
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
                }
            )
            async def get_courses(category: str):
                # Function implementation
                pass
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            
            self.register_function(name, description, wrapper, parameters)
            return wrapper
        return decorator

# Create global function router instance
function_router = FunctionRouter() 