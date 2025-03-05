from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import select
from app.models.user import User
from app.models.course import Course, Module, LectureContent, Lecture, CourseEnrollment, LectureContentDoc
from pydantic import BaseModel, EmailStr
from typing import Optional
import bcrypt
import uuid

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str = "student" # Default role
    password: str
    picture: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: Optional[str] = None
    picture: Optional[str] = None


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    user_dict = user_data.model_dump(exclude_unset=True)  # Remove unset fields
    user = User(**user_dict)
    user.hashed_password = bcrypt.hashpw(
        user_data.password.encode('utf-8'),
        bcrypt.gensalt()).decode('utf-8')
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_dict = user_data.model_dump(exclude_unset=True)  # Remove unset fields
    if "password" in update_dict:
        update_dict["hashed_password"] = bcrypt.hashpw(
            update_dict.pop("password").encode('utf-8'),
            bcrypt.gensalt()).decode('utf-8')
    for key, value in update_dict.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user_id: int):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}

async def get_all_user_courses(db: AsyncSession, user_id: uuid.UUID):
    """
    Get all Courses for a specificed user.
    
    Args:
        db: Database session
        user_id: user id of the faculty
        
    Returns:
        List of Courses with their details
    """
    try:
        query = (
        select(Course)
        .join(CourseEnrollment, Course.id == CourseEnrollment.course_id)
        .where(CourseEnrollment.student_id == user_id)
        )
        result = await db.execute(query)
        courses = result.scalars().all()
        
        return [course.to_dict() for course in courses]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
