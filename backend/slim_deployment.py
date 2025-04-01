"""
This script reduces the size of the Python deployment package by removing unnecessary files.
It should be run after dependencies are installed but before the package is deployed.
"""

import os
import shutil
import sys
from pathlib import Path

def reduce_package_size():
    """Remove unnecessary files to reduce deployment size."""
    print("Optimizing package size for deployment...")
    
    # Get the site-packages directory
    lib_path = None
    for path in sys.path:
        if path.endswith('site-packages'):
            lib_path = path
            break
    
    if not lib_path:
        print("Could not find site-packages directory")
        return
    
    site_packages = Path(lib_path)
    
    # Files and directories to remove
    to_remove = [
        # Tests directories
        "**/tests/",
        "**/test/",
        "**/__pycache__/",
        # Documentation
        "**/docs/",
        "**/doc/",
        "**/examples/",
        # Development files
        "**/.git/",
        "**/.github/",
        # Compiled extensions for other platforms
        "**/*.so",
        "**/*.dll",
        "**/*.dylib",
        # Type stubs
        "**/*.pyi",
        # Jupyter notebooks
        "**/*.ipynb",
        # Source maps
        "**/*.js.map",
    ]
    
    # Remove large packages we know we don't need
    specific_packages = [
        # Add specific package directories that can be safely removed
        "langchain",
        "langchain_*",
        "langgraph*",
        "numpy",
        "pandas",
        "jupyter",
        "ipython",
        "matplotlib",
        "boto3",
        "botocore"
    ]
    
    # Remove files and directories
    for pattern in to_remove:
        for path in site_packages.glob(pattern):
            if path.exists():
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    print(f"Removed: {path}")
                except Exception as e:
                    print(f"Failed to remove {path}: {e}")
    
    # Remove specific packages
    for package in specific_packages:
        for path in site_packages.glob(package):
            if path.exists() and path.is_dir():
                try:
                    shutil.rmtree(path)
                    print(f"Removed package: {path}")
                except Exception as e:
                    print(f"Failed to remove package {path}: {e}")
    
    print("Package optimization completed")

if __name__ == "__main__":
    reduce_package_size() 