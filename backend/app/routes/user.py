from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from app.database import get_db
from app.services.auth_service import get_current_user, require_auth
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class UserProfileUpdate(BaseModel):
    """
    Schema for user profile updates.
    
    This model defines the structure for updating a user's profile information.
    All fields are optional, allowing partial updates to the profile.
    
    Attributes:
        name: The user's display name
        email: The user's email address
        picture: URL to the user's profile picture
    """
    name: str | None = Field(
        None, 
        description="User's display name", 
        example="John Doe",
        min_length=1,
        max_length=100
    )
    email: str | None = Field(
        None, 
        description="User's email address", 
        example="john.doe@example.com",
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"
    )
    picture: str | None = Field(
        None, 
        description="URL to user's profile picture", 
        example="https://example.com/profile.jpg"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "picture": "https://example.com/profile.jpg"
            }
        }

@router.get("/user/profile", 
    summary="Get user profile",
    description="Retrieves the current user's profile information including ID, email, name, role, and profile picture",
    response_description="User profile data",
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "name": "John Doe",
                        "role": "student",
                        "picture": "https://example.com/profile.jpg"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - User not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        }
    }
)
async def get_user_profile(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Get the current user's profile information.
    
    This endpoint returns the complete profile information for the currently authenticated user.
    The profile includes the user's unique ID, email address, display name, assigned role
    (student, faculty, or support), and profile picture URL if available.
    
    The user is identified through the JWT token provided in the Authorization header.
    
    Args:
        request: The incoming request object
        db: Database session for potential database operations
        user: The authenticated user information extracted from the JWT token
        
    Returns:
        JSON response with user profile information
        
    Raises:
        HTTPException: 401 error if the user is not authenticated
    """
    return user

@router.put("/user/profile", 
    summary="Update user profile",
    description="Updates the current user's profile information with the provided data",
    response_description="Updated user profile data",
    responses={
        200: {
            "description": "User profile updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "updated@example.com",
                        "name": "Updated Name",
                        "role": "student",
                        "picture": "https://example.com/new-profile.jpg"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - User not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        },
        422: {
            "description": "Validation Error - Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "value is not a valid email address",
                                "type": "value_error.email"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Update the current user's profile information.
    
    This endpoint allows users to update their profile information by providing
    new values for one or more profile fields. Only the fields included in the
    request will be updated; omitted fields will retain their current values.
    
    The user is identified through the JWT token provided in the Authorization header.
    
    Note: This endpoint does not currently update the database directly. It only
    updates the user information in the session. A more complete implementation
    would persist these changes to the database.
    
    Args:
        profile_update: The updated profile information (partial updates supported)
        request: The incoming request object
        db: Database session for potential database operations
        user: The authenticated user information extracted from the JWT token
        
    Returns:
        JSON response with the complete updated user profile information
        
    Raises:
        HTTPException: 401 error if the user is not authenticated
        ValidationError: 422 error if the provided data fails validation
    """
    # Update only provided fields
    for field, value in profile_update.dict(exclude_unset=True).items():
        if value is not None:
            user[field] = value
    
    request.session["user"] = user
    return user
