#!/bin/bash

# Script to set up the test environment

echo "Setting up test environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo "Python version: $PYTHON_VERSION"

# Check if Python 3.13 is being used
if [[ $PYTHON_VERSION == *"3.13"* ]]; then
    echo "Python 3.13 detected. Installing compatible dependencies..."
    
    # Install compatible versions of dependencies
    pip install bcrypt==4.0.1
    pip install pydantic>=2.7.4
    pip install pydantic-settings>=2.0.0
    
    # Create a modified requirements file without pytest-profiling
    echo "Creating Python 3.13 compatible requirements file..."
    grep -v "pytest-profiling" requirements-test.txt > requirements-test-py313.txt
    
    # Install test dependencies from the modified file
    echo "Installing test dependencies..."
    pip install -r requirements-test-py313.txt
    
    # Clean up
    rm requirements-test-py313.txt
    
    echo "Python 3.13 compatibility patches will be applied automatically."
else
    echo "Using Python version other than 3.13. Standard dependencies will be installed."
    
    # Install test dependencies
    echo "Installing test dependencies..."
    pip install -r requirements-test.txt
fi

# Create test directories
echo "Creating test directories..."
mkdir -p tests/test_uploads
mkdir -p tests/test_uploads/assignments

# Set permissions
echo "Setting permissions..."
chmod +x run_tests.sh

echo "Test environment setup complete!"
echo ""
echo "To run tests, use:"
echo "./run_tests.sh"
echo ""
echo "For more options, run:"
echo "./run_tests.sh --help" 