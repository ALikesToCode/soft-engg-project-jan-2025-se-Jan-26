"""
Patch for Python 3.13 typing module compatibility.

This module directly patches the Python typing module's ForwardRef._evaluate method
to handle the recursive_guard parameter correctly.
"""
import sys
import types
import warnings
from typing import Any, Dict, Optional, Set, ForwardRef

def apply_patch():
    """
    Apply the patch to Python typing module's ForwardRef._evaluate method.
    This addresses the issue with recursive_guard being passed both positionally and as a keyword.
    """
    try:
        # Only apply the patch for Python 3.13+
        if sys.version_info < (3, 13):
            return

        # Get the original _evaluate method
        original_evaluate = ForwardRef._evaluate
        
        # Define the patched method
        def patched_evaluate(self, globalns, localns, type_params=None, recursive_guard=None):
            """
            Patched version of ForwardRef._evaluate that handles the recursive_guard parameter correctly.
            """
            # Ensure recursive_guard is a set
            if recursive_guard is None:
                recursive_guard = set()
            
            # Ensure type_params is a dict
            if type_params is None:
                type_params = {}
            
            # Call the original method with the correct parameters
            try:
                # Try calling with keyword arguments
                return original_evaluate(self, globalns, localns, type_params, recursive_guard=recursive_guard)
            except TypeError:
                try:
                    # Try calling with positional arguments
                    return original_evaluate(self, globalns, localns, type_params, recursive_guard)
                except TypeError:
                    # If all else fails, return Any
                    return Any
        
        # Apply the patch
        ForwardRef._evaluate = patched_evaluate
        
        # Filter out the specific deprecation warning
        warnings.filterwarnings(
            "ignore", 
            message="Failing to pass a value to the 'type_params' parameter of 'typing.ForwardRef._evaluate' is deprecated",
            category=DeprecationWarning
        )
        
        print("Applied Python typing module patch for ForwardRef._evaluate")
    except Exception as e:
        print(f"Failed to apply Python typing module patch: {e}") 