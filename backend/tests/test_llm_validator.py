import pytest
from pydantic import ValidationError
from app.validators.llm_validator import LLMInputValidator

def test_valid_input():
    """Test that valid input passes validation"""
    validator = LLMInputValidator(query="What courses are available?", max_tokens=1024)
    assert validator.query == "What courses are available?"
    assert validator.max_tokens == 1024

def test_empty_query():
    """Test that empty queries are rejected"""
    with pytest.raises(ValidationError):
        LLMInputValidator(query="", max_tokens=1024)
    
    with pytest.raises(ValidationError):
        LLMInputValidator(query="   ", max_tokens=1024)
    
def test_query_length():
    """Test query length validation"""
    # Test maximum length
    long_query = "a" * 2001
    with pytest.raises(ValidationError):
        LLMInputValidator(query=long_query)

def test_max_tokens_validation():
    """Test max_tokens validation"""
    # Test invalid max_tokens values
    with pytest.raises(ValidationError):
        LLMInputValidator(query="Valid query", max_tokens=0)
    
    with pytest.raises(ValidationError):
        LLMInputValidator(query="Valid query", max_tokens=3000)

def test_sql_injection_prevention():
    """Test that SQL injection attempts are caught"""
    sql_queries = [
        "SELECT * FROM users",
        "DROP TABLE students",
        "DELETE FROM courses",
        "'; DROP TABLE users; --",
        "UNION SELECT password FROM users",
    ]
    
    for query in sql_queries:
        with pytest.raises(ValueError):
            validator = LLMInputValidator(query=query)
            validator.validate_query(query)

def test_command_injection_prevention():
    """Test that command injection attempts are caught"""
    command_queries = [
        "ls; rm -rf /",
        "echo `rm -rf /`",
        "$(cat /etc/passwd)",
        "& whoami",
        "| cat /etc/shadow",
    ]
    
    for query in command_queries:
        with pytest.raises(ValueError):
            validator = LLMInputValidator(query=query)
            validator.validate_query(query)

def test_xss_prevention():
    """Test that XSS attempts are rejected"""
    xss_query = '<script>alert("XSS")</script>'
    with pytest.raises(ValueError):
        validator = LLMInputValidator(query=xss_query)

def test_schema_compliance():
    """Test schema compliance validation"""
    # Valid input should comply with schema
    validator = LLMInputValidator(query="Valid query")
    assert validator.validate_schema_compliance() is True
    
    # Test that extra fields are rejected
    with pytest.raises(ValidationError):
        LLMInputValidator(query="Valid query", invalid_field="test")

def test_input_sanitization():
    """Test input sanitization"""
    # Test whitespace normalization
    validator = LLMInputValidator(query="  Multiple    Spaces   Here  ")
    assert validator.sanitize_input() == "Multiple Spaces Here"
    
    # Test control character removal
    validator = LLMInputValidator(query="Line1\nLine2\tTab")
    sanitized = validator.sanitize_input()
    assert "\n" not in sanitized
    assert "\t" not in sanitized 