from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid


class FAQBase(BaseModel):
    """Base FAQ schema with common attributes."""
    question: str = Field(
        ..., 
        description="The frequently asked question", 
        min_length=5, 
        max_length=500,
        json_schema_extra={"example": "How do I submit an assignment?"}
    )
    answer: str = Field(
        ..., 
        description="The answer to the question", 
        min_length=5,
        json_schema_extra={"example": "You can submit your assignment by navigating to the assignment page and clicking the 'Submit' button."}
    )
    category_id: str = Field(
        ..., 
        description="Category identifier (general, technical, courses, account, faculty)",
        json_schema_extra={"example": "general"}
    )
    priority: Optional[int] = Field(
        0, 
        description="Display priority (higher numbers appear first)",
        json_schema_extra={"example": 10}
    )


class FAQCreate(FAQBase):
    """Schema for creating a new FAQ."""
    question: str = Field(None, description="The frequently asked question", min_length=5, max_length=500)
    answer: str = Field(None, description="The answer to the question", min_length=5)
    category_id: str = Field(None, description="Category identifier (general, technical, courses, account, faculty)")
    priority: int = Field(None, description="Display priority (higher numbers appear first)")


class FAQUpdate(BaseModel):
    """Schema for updating an existing FAQ."""
    question: Optional[str] = Field(None, description="The frequently asked question", min_length=5, max_length=500)
    answer: Optional[str] = Field(None, description="The answer to the question", min_length=5)
    category_id: Optional[str] = Field(None, description="Category identifier (general, technical, courses, account, faculty)")
    priority: Optional[int] = Field(None, description="Display priority (higher numbers appear first)")


class FAQInDB(FAQBase):
    """Schema for FAQ as stored in the database."""
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FAQResponse(FAQInDB):
    """Schema for FAQ response."""
    pass


class FAQRating(BaseModel):
    """Schema for rating an FAQ."""
    is_helpful: bool = Field(..., description="Whether the FAQ was helpful or not")


class FAQSearchQuery(BaseModel):
    """Schema for searching FAQs."""
    query: str = Field(..., description="Search query string", min_length=2)
    limit: int = Field(20, description="Maximum number of results to return") 