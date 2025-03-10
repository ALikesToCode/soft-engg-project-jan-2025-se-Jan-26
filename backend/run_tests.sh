#!/bin/bash

# Set environment variables for testing
export TESTING=True
# Use the existing PostgreSQL database for testing
# export DATABASE_URL="sqlite+aiosqlite:///./test.db?mode=rwc"
export JWT_SECRET_KEY="test_secret_key_for_testing_purposes_only"
export JWT_ALGORITHM="HS256"
export JWT_EXPIRATION=3600
export UPLOAD_DIR="./test_uploads"
export REDIS_URL="redis://redis-19669.c264.ap-south-1-1.ec2.redns.redis-cloud.com:19669"

# Create test uploads directory if it doesn't exist
mkdir -p ./test_uploads
chmod -R 775 ./test_uploads

# Run the tests with pytest
echo "Running tests..."
python -m pytest tests/ -v -o asyncio_default_fixture_loop_scope=function

# Clean up test uploads directory
echo "Cleaning up test uploads..."
rm -rf ./test_uploads

echo "Tests completed!" 