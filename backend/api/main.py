"""
Vercel Serverless Function Entry Point

This file serves as the entry point for Vercel serverless functions.
It imports the main FastAPI application from the parent directory.
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI application from the parent directory
from main import app

# This variable is used by Vercel to locate your application
app = app 