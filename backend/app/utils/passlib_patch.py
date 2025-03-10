"""
Patch for passlib compatibility with newer bcrypt versions.

This module patches the passlib bcrypt handler to fix the version detection issue
with newer versions of bcrypt that don't have the __about__ attribute.
"""
import warnings
import importlib.util
import sys

def apply_patch():
    """
    Apply the patch to passlib bcrypt handler to fix the version detection issue.
    """
    try:
        # Import the modules that need patching
        import bcrypt
        import passlib.handlers.bcrypt as passlib_bcrypt
        
        # Check if bcrypt has the __about__ attribute
        if not hasattr(bcrypt, '__about__'):
            # Get the version directly from bcrypt
            bcrypt_version = getattr(bcrypt, '__version__', '4.0.1')
            
            # Create a fake __about__ module with __version__ attribute
            class FakeAbout:
                __version__ = bcrypt_version
            
            # Attach the fake __about__ module to bcrypt
            bcrypt.__about__ = FakeAbout()
            
            # Monkey patch the _load_backend_mixin function if it exists
            if hasattr(passlib_bcrypt, '_load_backend_mixin'):
                original_load_backend_mixin = passlib_bcrypt._load_backend_mixin
                
                def patched_load_backend_mixin(name):
                    """
                    Patched version of _load_backend_mixin that handles newer bcrypt versions.
                    """
                    if name == "bcrypt":
                        return bcrypt
                    else:
                        return original_load_backend_mixin(name)
                
                passlib_bcrypt._load_backend_mixin = patched_load_backend_mixin
            
            # Filter out the specific warning
            warnings.filterwarnings(
                "ignore", 
                message="error reading bcrypt version",
                category=UserWarning,
                module="passlib.handlers.bcrypt"
            )
            
            print(f"Applied passlib bcrypt patch for bcrypt version {bcrypt_version}")
    except ImportError as e:
        # If the modules are not available, we don't need to patch
        print(f"Skipping passlib bcrypt patch: {e}")
    except Exception as e:
        print(f"Failed to apply passlib bcrypt patch: {e}") 