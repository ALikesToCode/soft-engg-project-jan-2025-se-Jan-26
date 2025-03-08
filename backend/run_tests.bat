@echo off
REM Set environment variables for testing
set TESTING=True
set DATABASE_URL=sqlite+aiosqlite:///./test.db
set JWT_SECRET_KEY=test_secret_key_for_testing_purposes_only
set JWT_ALGORITHM=HS256
set JWT_EXPIRATION=3600
set UPLOAD_DIR=.\test_uploads
set REDIS_URL=redis://localhost:6379/0

REM Remove test database if it exists
if exist ".\test.db" del /F /Q ".\test.db"

REM Create test uploads directory if it doesn't exist
if not exist ".\test_uploads" mkdir ".\test_uploads"

REM Run the tests with pytest
echo Running tests...
python -m pytest tests/ -v -o asyncio_default_fixture_loop_scope=function

REM Clean up test uploads directory
echo Cleaning up test uploads...
rmdir /S /Q ".\test_uploads"

REM Remove test database
if exist ".\test.db" del /F /Q ".\test.db"

echo Tests completed!
pause
