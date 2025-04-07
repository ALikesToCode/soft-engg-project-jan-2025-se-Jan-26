from pydantic import BaseModel, Field, field_validator, ConfigDict
import re
import logging
from typing import Optional
from html import escape

logger = logging.getLogger(__name__)

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
        # Log the incoming value for debugging
        logger.info(f"Validating query input: {repr(v)}")
        
        # Check for None
        if v is None:
            logger.error("Query is None")
            raise ValueError("Query cannot be None")
        
        # Check for empty string
        if not v:
            logger.error("Query is empty string")
            raise ValueError("Query cannot be empty")
        
        # Remove any null bytes
        if '\x00' in v:
            logger.warning("Query contains null bytes, removing them")
            v = v.replace('\x00', '')
        
        # Check for empty query after trimming
        if not v.strip():
            logger.error("Query contains only whitespace")
            raise ValueError("Query cannot be empty or contain only whitespace")
        
        # Basic XSS protection
        v_original = v
        v = escape(v)
        if v != v_original:
            logger.warning("Query contains HTML special chars that were escaped")
        
        # Remove any potential SQL injection patterns
        sql_patterns = [
            r'(?i)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)',
            r'(?i)(--|;|/\*|\*/)',
            r'(?i)(exec\s+xp_)',
            r'(?i)(WAITFOR\s+DELAY)',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, v):
                logger.warning(f"Query contains potential SQL pattern: {pattern}")
                raise ValueError("Invalid characters or patterns detected in query")
        
        # Remove any potential command injection patterns
        injection_chars = ['&', '|', ';', '`', '$', '(', ')']
        if any(char in v for char in injection_chars):
            found_chars = [char for char in injection_chars if char in v]
            logger.warning(f"Query contains potential command injection chars: {found_chars}")
            raise ValueError("Invalid characters detected in query")
        
        logger.info(f"Query validation successful: {v.strip()}")
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
        except Exception as e:
            logger.error(f"Schema validation error: {str(e)}")
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