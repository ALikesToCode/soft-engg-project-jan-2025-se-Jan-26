# Assignment Management System Tests

This directory contains tests for the Assignment Management System backend. The tests are organized by module and functionality.

## Test Structure

- `conftest.py`: Contains fixtures and setup for all tests
- `test_assignment_models.py`: Tests for the Assignment and Submission models
- `test_assignment_service.py`: Tests for the assignment service functions
- `test_assignment_routes.py`: Tests for the assignment API endpoints
- `test_assignment_api.py`: Integration tests for the assignment API
- `test_assignment_basic.py`: Basic tests for assignment models and schemas
- `test_auth.py`: Tests for authentication functionality
- `test_llm.py`: Tests for LLM integration and function calling
- `test_llm_validator.py`: Tests for LLM input validation
- `test_analytics_service.py`: Tests for analytics service
- `test_api_endpoints.py`: Tests for general API endpoints
- `test_services.py`: Tests for various service functions
- `test_academic_integrity.py`: Tests for academic integrity endpoints
- `test_chat.py`: Tests for chat and function calling endpoints

## Running Tests

You can run the tests using the provided script:

```bash
# From the backend directory
./run_tests.sh
```

Or manually with pytest:

```bash
# Set environment variables
export TESTING=True
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export JWT_SECRET_KEY="test_secret_key_for_testing_purposes_only"
export JWT_ALGORITHM="HS256"
export JWT_EXPIRATION=3600
export UPLOAD_DIR="./test_uploads"
export REDIS_URL="redis://localhost:6379/0"

# Run tests
python -m pytest tests/ -v
```

To run specific test files:

```bash
# Run a specific test file
python -m pytest tests/test_auth.py -v

# Run tests with specific markers
python -m pytest tests/ -m "asyncio" -v

# Run tests with coverage report
python -m pytest tests/ --cov=app --cov-report=term-missing
```

## Test Coverage

### Authentication Tests (`test_auth.py`)

- Email/password login
- Google OAuth authentication
- User information retrieval
- Token refresh
- Logout functionality
- Password management (set/reset)
- Email verification

### Assignment Model Tests (`test_assignment_models.py`, `test_assignment_basic.py`)

- Assignment model creation and validation
- Submission model creation and validation
- Late submission calculation
- Assignment status transitions
- Schema validation

### Assignment Service Tests (`test_assignment_service.py`)

- Creating assignments
- Retrieving assignments (by ID, by course)
- Updating assignments
- Deleting assignments
- Creating submissions
- Retrieving submissions
- Grading submissions
- Plagiarism checking

### Assignment API Tests (`test_assignment_api.py`, `test_assignment_routes.py`)

- Assignment creation API
- Assignment retrieval API
- Assignment update API
- Assignment deletion API
- Submission creation API
- Submission retrieval API
- Submission grading API
- Plagiarism report API

### LLM Integration Tests (`test_llm.py`, `test_llm_validator.py`)

- LLM input validation
- Chat functionality
- Function calling
- Error handling
- Web search integration
- Input sanitization
- Security validation (SQL injection, XSS, etc.)

### Chat Endpoint Tests (`test_chat.py`)

- Chat history retrieval
- Basic chat functionality
- Function calling in chat
- Error handling in chat
- Web search function
- Available functions retrieval
- Direct function execution

### Academic Integrity Tests (`test_academic_integrity.py`)

- Flagged interactions retrieval
- Flag status updates
- Flag escalation
- Flag statistics
- Flag audit trail
- LLM request validation
- Submission flagging
- Flag retrieval and updates

### API Endpoint Tests (`test_api_endpoints.py`)

- Root endpoint
- Health endpoint
- Metrics endpoint
- Logs endpoint
- Alerts management
- System summary
- Service status
- Dashboard data

### Analytics Tests (`test_analytics_service.py`)

- Student performance analytics
- Course analytics
- Assignment analytics
- Submission statistics

## Test Fixtures

The `conftest.py` file provides several fixtures that can be used across tests:

- `client`: FastAPI TestClient for synchronous requests
- `async_client`: AsyncClient for asynchronous requests
- `db_session`: Database session for direct database operations
- `test_users`: Pre-created faculty and student users
- `tokens`: JWT tokens for faculty and student users
- `test_assignment`: Sample assignment for testing
- `test_submission`: Sample submission for testing

## Mocking

Many tests use the `unittest.mock` library to mock external dependencies:

- Database operations
- External API calls
- LLM responses
- Email sending
- File operations

## Adding New Tests

When adding new tests:

1. Use the existing fixtures in `conftest.py` where possible
2. Follow the naming convention `test_*` for test functions
3. Group related tests in the same file
4. Use descriptive test names that explain what is being tested
5. Add appropriate assertions to verify expected behavior
6. Use `@pytest.mark.asyncio` for asynchronous tests
7. Use `@pytest.mark.parametrize` for testing multiple inputs
8. Use mocking to isolate the code being tested

## Continuous Integration

These tests are run automatically in the CI/CD pipeline on every pull request and merge to the main branch. All tests must pass before code can be merged. 