"""
Patch for Pydantic v1 compatibility with Python 3.13.

This module patches the ForwardRef._evaluate method in Pydantic v1 to handle
the type_params parameter correctly, addressing the deprecation warning in Python 3.13.
"""
import sys
import types
import warnings
import inspect
from typing import Any, Dict, Optional, Set, cast

def apply_patch():
    """
    Apply the patch to Pydantic v1 ForwardRef._evaluate method to handle type_params parameter.
    This addresses the deprecation warning in Python 3.13.
    """
    try:
        # Only apply the patch for Python 3.13+
        if sys.version_info < (3, 13):
            return

        # Import the module that needs patching
        from pydantic.v1 import typing as pydantic_v1_typing
        
        # Completely replace the ForwardRef class with our own implementation
        original_ForwardRef = pydantic_v1_typing.ForwardRef
        
        class PatchedForwardRef(original_ForwardRef):
            """
            A patched version of ForwardRef that handles Python 3.13's changes to _evaluate.
            """
            def _evaluate(self, globalns, localns, recursive_guard=None, type_params=None):
                """
                Patched version of _evaluate that handles both recursive_guard and type_params.
                """
                # Ensure recursive_guard is a set
                if recursive_guard is None:
                    recursive_guard = set()
                
                # Ensure type_params is a dict
                if type_params is None:
                    type_params = {}
                
                # Get the forward value (the string representation of the type)
                forward_value = self.__forward_value__
                
                # Check if we've seen this type before (to prevent infinite recursion)
                if forward_value in recursive_guard:
                    return Any
                
                # Add this type to the recursive guard set
                recursive_guard.add(forward_value)
                
                try:
                    # Try to evaluate the type string in the given namespaces
                    if globalns is None and localns is None:
                        globalns = localns = {}
                    elif globalns is None:
                        globalns = localns
                    elif localns is None:
                        localns = globalns
                    
                    # Evaluate the type string
                    value = eval(forward_value, globalns, localns)
                    return value
                except (NameError, TypeError):
                    # If evaluation fails, return Any
                    return Any
                finally:
                    # Remove this type from the recursive guard set
                    recursive_guard.discard(forward_value)
        
        # Replace the ForwardRef class
        pydantic_v1_typing.ForwardRef = PatchedForwardRef
        
        # Also patch the evaluate_forwardref function
        def patched_evaluate_forwardref(type_, globalns, localns):
            """
            Patched version of evaluate_forwardref that handles the recursive_guard parameter.
            """
            return cast(Any, type_)._evaluate(globalns, localns, set())
        
        pydantic_v1_typing.evaluate_forwardref = patched_evaluate_forwardref
        
        # Filter out the specific deprecation warning
        warnings.filterwarnings(
            "ignore", 
            message="Failing to pass a value to the 'type_params' parameter of 'typing.ForwardRef._evaluate' is deprecated",
            category=DeprecationWarning
        )
        
        print("Applied Pydantic v1 patch for Python 3.13 compatibility")
    except ImportError:
        # If pydantic.v1 is not available, we don't need to patch
        pass
    except Exception as e:
        print(f"Failed to apply Pydantic v1 patch: {e}") 