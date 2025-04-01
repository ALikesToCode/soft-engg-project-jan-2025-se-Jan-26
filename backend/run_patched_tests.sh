#!/bin/bash

# Script to run tests with patches applied:
# 1. Pydantic v1 patch for Python 3.13 compatibility
# 2. Passlib bcrypt patch for newer bcrypt versions

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set environment variables for testing
export TESTING=1
export PYTHONPATH=$PWD

# Run pytest with warnings filtered
python -m pytest tests/ -v

# Deactivate virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 