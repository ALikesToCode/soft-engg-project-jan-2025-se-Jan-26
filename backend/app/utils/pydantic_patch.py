"""
Patch for Pydantic v1 compatibility with Python 3.13.

This module patches the ForwardRef._evaluate method in Pydantic v1 to handle
the type_params parameter correctly, addressing the deprecation warning in Python 3.13.
"""
import sys
import types
import warnings
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
        
        # Get the original _evaluate method
        original_evaluate = pydantic_v1_typing.ForwardRef._evaluate
        
        # Define the patched method
        def patched_evaluate(self, globalns: Optional[Dict[str, Any]], localns: Optional[Dict[str, Any]], 
                             recursive_guard: Optional[Set[Any]] = None, type_params=None):
            """
            Patched version of ForwardRef._evaluate that includes the type_params parameter.
            """
            # Ensure recursive_guard is a set
            if recursive_guard is None:
                recursive_guard = set()
            
            # In Python 3.13, ForwardRef._evaluate expects type_params
            if type_params is None:
                type_params = {}
                
            try:
                # Try calling with both parameters
                return original_evaluate(self, globalns, localns, recursive_guard=recursive_guard, type_params=type_params)
            except TypeError:
                # If that fails, try with just recursive_guard
                try:
                    return original_evaluate(self, globalns, localns, recursive_guard=recursive_guard)
                except TypeError:
                    # If that also fails, try with positional arguments
                    return original_evaluate(self, globalns, localns, recursive_guard)
        
        # Apply the patch
        pydantic_v1_typing.ForwardRef._evaluate = patched_evaluate
        
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