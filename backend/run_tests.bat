@echo off
REM Set environment variables for testing
set TESTING=True
REM Use the existing PostgreSQL database for testing
REM set DATABASE_URL=sqlite+aiosqlite:///./test.db?mode=rwc
set JWT_SECRET_KEY=test_secret_key_for_testing_purposes_only
set JWT_ALGORITHM=HS256
set JWT_EXPIRATION=3600
set UPLOAD_DIR=./test_uploads
set REDIS_URL=redis://redis-19669.c264.ap-south-1-1.ec2.redns.redis-cloud.com:19669

REM Create test uploads directory if it doesn't exist
if not exist .\test_uploads mkdir .\test_uploads

REM Run the tests with pytest
echo Running tests...
python -m pytest tests/ -v -o asyncio_default_fixture_loop_scope=function

REM Clean up test uploads directory
echo Cleaning up test uploads...
if exist .\test_uploads rmdir /s /q .\test_uploads

echo Tests completed!
