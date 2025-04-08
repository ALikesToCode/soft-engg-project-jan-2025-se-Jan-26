from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from app.models.user import UserRole
import uuid
from datetime import datetime

class UserBase(BaseModel):
    """Base model for user-related schemas"""
    email: EmailStr
    name: str

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8)
    role: Optional[UserRole] = None

class UserRegister(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8)
    role: Optional[UserRole] = None

class UserLogin(BaseModel):
    """Schema for user login credentials"""
    email: EmailStr
    password: str

class UserOut(UserBase):
    """Schema for returning user information"""
    id: uuid.UUID
    role: UserRole
    created_at: datetime
    last_active: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = None
    role: Optional[UserRole] = None

class UserChangePassword(BaseModel):
    """Schema for changing user password"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def passwords_must_be_different(cls, v, values):
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('New password must be different from current password')
        return v

class UserList(BaseModel):
    """Schema for paginated list of users"""
    items: List[UserOut]
    total: int
    page: int
    per_page: int
    pages: int

class UserPasswordReset(BaseModel):
    """Schema for resetting user password"""
    token: str
    new_password: str = Field(..., min_length=8)

class UserForgotPassword(BaseModel):
    """Schema for initiating password reset"""
    email: EmailStr 