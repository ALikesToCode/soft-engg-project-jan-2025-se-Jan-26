from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: str
    name: str
    role: str
    picture: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    """User response schema for API responses"""
    id: str
    
    @classmethod
    def from_orm(cls, obj):
        if hasattr(obj, 'id') and obj.id and not isinstance(obj.id, str):
            obj.id = str(obj.id)
        return super().from_orm(obj)

# Add an alias for User that points to UserResponse to fix import issues
User = UserResponse

class UpdateUserRequest(BaseModel):
    """Schema for updating user data"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    picture: Optional[str] = None
    role: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class CourseBase(BaseModel):
    """Base course schema with common fields"""
    name: str
    code: str
    title: str
    description: Optional[str] = None
    credits: int
    
    model_config = ConfigDict(from_attributes=True)

class CourseResponse(CourseBase):
    """Course response schema for API responses"""
    id: str
    created_at: datetime
    updated_at: datetime
    progress: Optional[float] = None
    last_activity: Optional[datetime] = None
    is_favorited: Optional[bool] = None
    
    @classmethod
    def from_orm(cls, obj):
        if hasattr(obj, 'id') and obj.id and not isinstance(obj.id, str):
            obj.id = str(obj.id)
        return super().from_orm(obj)

class BookmarkedMaterialResponse(BaseModel):
    """Response schema for bookmarked materials"""
    id: str
    user_id: str
    course_id: str
    material_id: str
    material_type: str
    title: str
    description: Optional[str] = None
    date_bookmarked: datetime
    meta_data: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm(cls, obj):
        if hasattr(obj, 'id') and obj.id and not isinstance(obj.id, str):
            obj.id = str(obj.id)
        if hasattr(obj, 'user_id') and obj.user_id and not isinstance(obj.user_id, str):
            obj.user_id = str(obj.user_id)
        if hasattr(obj, 'course_id') and obj.course_id and not isinstance(obj.course_id, str):
            obj.course_id = str(obj.course_id)
        if hasattr(obj, 'material_id') and obj.material_id and not isinstance(obj.material_id, str):
            obj.material_id = str(obj.material_id)
        return super().from_orm(obj)

class UserRecommendedCourseResponse(BaseModel):
    """Response schema for recommended courses"""
    id: str
    user_id: str
    course_id: str
    recommendation_date: datetime
    relevance_score: float
    reason: Optional[str] = None
    source: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm(cls, obj):
        if hasattr(obj, 'id') and obj.id and not isinstance(obj.id, str):
            obj.id = str(obj.id)
        if hasattr(obj, 'user_id') and obj.user_id and not isinstance(obj.user_id, str):
            obj.user_id = str(obj.user_id)
        if hasattr(obj, 'course_id') and obj.course_id and not isinstance(obj.course_id, str):
            obj.course_id = str(obj.course_id)
        return super().from_orm(obj) 