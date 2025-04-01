from pydantic import BaseModel, Field, field_validator, ConfigDict
import re
from typing import Optional
from html import escape

class LLMInputValidator(BaseModel):
    """
    Enhanced validator for LLM input with comprehensive validation and sanitization.
    
    Attributes:
        query: The user's message to send to the AI
        max_length: Optional maximum length for the query
    """
    query: str = Field(
        ..., 
        description="The user's message to the AI",
        min_length=1,
        max_length=2000  # Reasonable limit for most LLM APIs
    )
    max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum number of tokens for the response",
        ge=1,
        le=2048
    )

    # Validators
    @field_validator('query')
    def validate_query(cls, v):
        # Remove any null bytes
        v = v.replace('\x00', '')
        
        # Check for empty query after trimming
        if not v.strip():
            raise ValueError("Query cannot be empty or contain only whitespace")
        
        # Basic XSS protection
        v = escape(v)
        
        # Remove any potential SQL injection patterns
        sql_patterns = [
            r'(?i)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)',
            r'(?i)(--|;|/\*|\*/)',
            r'(?i)(exec\s+xp_)',
            r'(?i)(WAITFOR\s+DELAY)',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, v):
                raise ValueError("Invalid characters or patterns detected in query")
        
        # Remove any potential command injection patterns
        if any(char in v for char in ['&', '|', ';', '`', '$', '(', ')']):
            raise ValueError("Invalid characters detected in query")
        
        return v.strip()

    @field_validator('max_tokens')
    def validate_max_tokens(cls, v):
        if v is not None and (v < 1 or v > 2048):
            raise ValueError("max_tokens must be between 1 and 2048")
        return v

    def sanitize_input(self) -> str:
        """
        Sanitize the input query by applying various cleaning operations.
        
        Returns:
            str: The sanitized query string
        """
        # Convert to string and normalize whitespace
        sanitized = ' '.join(self.query.split())
        
        # Remove any control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
        
        # Encode special characters
        sanitized = escape(sanitized)
        
        return sanitized

    def validate_schema_compliance(self) -> bool:
        """
        Validate that the input complies with the expected schema.
        
        Returns:
            bool: True if the input is schema-compliant, False otherwise
        """
        try:
            # Validate using pydantic's built-in validation
            self.model_validate(self.model_dump())
            return True
        except Exception:
            return False

    # Pydantic v2 configuration
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",  # Forbid extra attributes
        json_schema_extra={
            "example": {
                "query": "What courses are available in the IITM program?",
                "max_tokens": 1024
            }
        }
    ) 