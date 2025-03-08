#!/bin/bash

# Set environment variables for testing
export TESTING=True
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export JWT_SECRET_KEY="test_secret_key_for_testing_purposes_only"
export JWT_ALGORITHM="HS256"
export JWT_EXPIRATION=3600
export UPLOAD_DIR="./test_uploads"
export REDIS_URL="redis://localhost:6379/0"

# Create test uploads directory if it doesn't exist
mkdir -p ./test_uploads

# Run the tests with pytest
echo "Running tests..."
python -m pytest tests/ -v

# Clean up test uploads directory
echo "Cleaning up test uploads..."
rm -rf ./test_uploads

echo "Tests completed!" 