# Assignment Management System Tests

This directory contains tests for the Assignment Management System backend. The tests are organized by module and functionality.

## Test Structure

- `conftest.py`: Contains fixtures and setup for all tests
- `test_assignment_models.py`: Tests for the Assignment and Submission models
- `test_assignment_service.py`: Tests for the assignment service functions
- `test_assignment_routes.py`: Tests for the assignment API endpoints
- `test_auth.py`: Tests for authentication functionality
- `test_llm.py`: Tests for LLM integration

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

## Test Coverage

### Assignment Models Tests

- Assignment model creation and validation
- Submission model creation and validation
- Late submission calculation
- Assignment status transitions

### Assignment Service Tests

- Creating assignments
- Retrieving assignments (by ID, by course)
- Updating assignments
- Deleting assignments
- Creating submissions
- Retrieving submissions
- Grading submissions
- Plagiarism checking

### Assignment Routes Tests

- Assignment creation API
- Assignment retrieval API
- Assignment update API
- Assignment deletion API
- Submission creation API
- Submission retrieval API
- Submission grading API
- Plagiarism report API

## Authentication

The tests use JWT tokens for authentication. Test fixtures provide tokens for both faculty and student roles to test permission-based access control.

## Database

Tests use an in-memory SQLite database to ensure they are isolated and don't affect any production data.

## File Uploads

For tests involving file uploads, a temporary directory (`./test_uploads`) is created and cleaned up after tests complete.

## Adding New Tests

When adding new tests:

1. Use the existing fixtures in `conftest.py` where possible
2. Follow the naming convention `test_*` for test functions
3. Group related tests in the same file
4. Use descriptive test names that explain what is being tested
5. Add appropriate assertions to verify expected behavior 