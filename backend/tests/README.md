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

## Optimized Test Setup

The test suite has been optimized for performance and compatibility with Python 3.13. Key optimizations include:

### Session-Scoped Fixtures

- Database schema and engine are created once per test session
- Test upload directories are created once per test session
- Dependency overrides are applied once per test session

### In-Memory SQLite Support

Tests can run with an in-memory SQLite database for faster execution:

```bash
# Enable SQLite for testing
export TEST_USE_SQLITE=true
```

### Parallel Test Execution

Tests can run in parallel using pytest-xdist:

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
python -m pytest tests/ -n auto
```

### Test Categorization

Tests are categorized using pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.api`: API tests
- `@pytest.mark.model`: Model tests
- `@pytest.mark.service`: Service tests
- `@pytest.mark.auth`: Authentication tests
- `@pytest.mark.llm`: LLM-related tests
- `@pytest.mark.chat`: Chat-related tests
- `@pytest.mark.academic_integrity`: Academic integrity tests
- `@pytest.mark.assignment`: Assignment-related tests
- `@pytest.mark.analytics`: Analytics-related tests
- `@pytest.mark.slow`: Slow tests

## Running Tests

You can run the tests using the provided script:

```bash
# From the backend directory
./run_tests.sh
```

The script supports various options:

```bash
# Run with coverage report
./run_tests.sh --coverage

# Run only unit tests
./run_tests.sh --unit

# Run failed tests first
./run_tests.sh --failed-first

# Skip slow tests
./run_tests.sh --not-slow

# Run specific test file
./run_tests.sh tests/test_auth.py

# Run with profiling
./run_tests.sh --profile
```

Or manually with pytest:

```bash
# Set environment variables
export TESTING=True
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export JWT_SECRET_KEY="test_secret_key_for_testing_purposes_only"
export JWT_ALGORITHM="HS256"
export JWT_EXPIRATION=3600
export UPLOAD_DIR="./tests/test_uploads"
export REDIS_URL="redis://localhost:6379/0"

# Run tests
python -m pytest tests/ -v
```

## Installing Test Dependencies

Install the required testing dependencies:

```bash
# Automatically install dependencies and set up the test environment
./setup_tests.sh

# Or manually install dependencies
pip install -r requirements-test.txt
```

This will install:
- pytest and pytest-asyncio
- pytest-xdist for parallel testing
- pytest-cov for coverage reports
- pytest-lazy-fixture for optimized fixture usage
- Compatible versions of bcrypt, pydantic, and pydantic-settings for Python 3.13

### Python 3.13 Compatibility Notes

When using Python 3.13, some packages have compatibility issues:

- **pytest-profiling**: Not compatible with Python 3.13 as it uses the removed `pipes` module. The `run_tests.sh` script automatically falls back to using Python's built-in `cProfile` for profiling when running with Python 3.13.

## Python 3.13 Compatibility

The test suite includes patches for compatibility with Python 3.13:

1. **Passlib Patch**: Fixes issues with bcrypt 4.x and passlib
2. **Pydantic Patch**: Fixes issues with Pydantic's ForwardRef evaluation
3. **Python Typing Patch**: Fixes issues with Python's typing module

For more information, see the `PYTHON_3_13_COMPATIBILITY.md` file in the backend directory.

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

- `test_schema`: Test schema name (session-scoped)
- `database_url`: Database URL for testing (session-scoped)
- `engine`: Database engine (session-scoped)
- `session_factory`: Session factory (session-scoped)
- `db_session`: Database session (function-scoped)
- `client`: FastAPI TestClient (function-scoped)
- `async_client`: AsyncClient for asynchronous requests (function-scoped)
- `test_users`: Pre-created faculty, student, and support users
- `tokens`: JWT tokens for faculty, student, and support users
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
9. Add appropriate markers to categorize your tests

## Performance Tips

1. **Use session-scoped fixtures** for expensive operations
2. **Use function-scoped fixtures** for test-specific data
3. **Use in-memory SQLite** for faster database tests
4. **Run tests in parallel** with pytest-xdist
5. **Skip slow tests** during development with `--not-slow`
6. **Profile tests** with built-in cProfile (Python 3.13) or pytest-profiling (Python < 3.13)
7. **Use test categories** to run only what you need

## Continuous Integration

These tests are run automatically in the CI/CD pipeline on every pull request and merge to the main branch. All tests must pass before code can be merged. 