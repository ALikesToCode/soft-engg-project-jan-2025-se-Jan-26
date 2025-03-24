from fastapi import APIRouter, Depends, HTTPException, Request, Query
from starlette.requests import Request
from app.database import get_db
from app.services.auth_service import get_current_user, require_auth, get_user
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import get_all_user_courses, fetch_user_course_content
from app.models.user import User
from sqlalchemy.future import select
from typing import List, Optional
import uuid

router = APIRouter(tags=["User"])

# User schema for response
class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    picture: str | None = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm(cls, obj):
        # Convert UUID to string
        if hasattr(obj, 'id') and obj.id:
            obj.id = str(obj.id)
        return super().from_orm(obj)

class UserProfile(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str  # e.g., "student", "faculty", "support"
    profile_pic_url: Optional[str] = None

# Add a new endpoint to get all users
@router.get("/users", 
    response_model=List[UserResponse],
    summary="Get all users",
    description="Retrieves all users in the system. Only accessible to faculty/admin users.",
    response_description="List of all users",
    responses={
        200: {
            "description": "Users retrieved successfully"
        },
        401: {
            "description": "Unauthorized - User not authenticated"
        },
        403: {
            "description": "Forbidden - User does not have required permissions"
        }
    }
)
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all users in the system.
    
    This endpoint returns a list of all users in the system. It is only accessible
    to users with faculty or admin roles.
    
    Args:
        db: Database session
        current_user: The authenticated user information
        
    Returns:
        List of user objects
        
    Raises:
        HTTPException: 401 error if the user is not authenticated
        HTTPException: 403 error if the user does not have required permissions
    """
    # Check if user has permission (faculty or admin)
    if current_user["role"] not in ["faculty", "admin", "support"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get all users from the database
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    # Convert User objects to dictionaries with string IDs
    user_list = []
    for user in users:
        user_dict = {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "picture": user.picture
        }
        user_list.append(user_dict)
    
    return user_list

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
        min_length=1,
        max_length=100,
        json_schema_extra={"example": "John Doe"}
    )
    email: str | None = Field(
        None, 
        description="User's email address", 
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
        json_schema_extra={"example": "john.doe@example.com"}
    )
    picture: str | None = Field(
        None, 
        description="URL to user's profile picture",
        json_schema_extra={"example": "https://example.com/profile.jpg"}
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "picture": "https://example.com/profile.jpg"
            }
        }
    )

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
    result = await db.execute(select(User).where(User.id == user["sub"]))
    user = result.scalars().first()

    if not user: 
        raise HTTPException(status_code=404, detail="User not found")

    user_profile = UserProfile(
        id=str(user.id),
        name=user.name, 
        email=user.email,
        role=user.role,
        profile_pic_url=user.picture 
    )
    return user_profile

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

@router.get("/user/courses",response_model=list[dict],
    summary="Get user courses",
    description="Retrieves all courses enrolled by the current user",
    response_description="List of user courses",
    responses={
        200: {
            "description": "User courses retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Course Name",
                            "code": "COURSE101",
                            "title": "Course Title",
                            "syllabus": "Course syllabus",
                            "description": "Course description",
                            "credits": 3,
                            "duration": 12,
                            "semester": "Spring",
                            "year": 2022,
                            "status": "active",
                            "created_at": "2022-01-01T12:00:00",
                            "updated_at": "2022-01-01T12:00:00"
                        }
                    ]
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
        500: {
            "description": "Internal Server Error - Failed to retrieve user courses",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error occurred"}
                }
            }
        }
    }
)
async def fetch_user_courses(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
    ):  
    try:
        # Get the user from the database based on the email in the token
        user = await get_user(db, current_user["email"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Use the user ID from the database
        courses = await get_all_user_courses(db, user.id)  
        return courses
    except Exception as e:
        print("Error=> ", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/course/content",response_model=dict)
async def get_user_course_content(
    course_id: uuid.UUID = Query(..., description="ID of the course to fetch"),
    db: AsyncSession = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    try:
        user = await get_user(db, current_user["email"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        course_content = await fetch_user_course_content(db,course_id)
        return course_content
    except Exception as e:
        print("Error=> ", e)
        raise HTTPException(status_code=500, detail=str(e))
