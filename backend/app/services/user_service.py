from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import select
from app.models.user import User
from app.models.course import Course, Module, LectureContent, Lecture, CourseEnrollment, LectureContentDoc, BookmarkedMaterials
from app.services.course_service import CourseService
from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from sqlalchemy.orm import selectinload
import bcrypt
import uuid
import logging
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


logger = logging.getLogger(__name__)

async def create_user(db: AsyncSession, user_data: UserCreate) -> uuid.UUID:
    # Check if a user with the given email already exists
    existing_user_query = select(User).where(User.email == user_data.email)
    result = await db.execute(existing_user_query)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")
    
    user_dict = user_data.model_dump(exclude_unset=True)  # Remove unset fields
    
    # Extract password from user_dict to handle it separately
    password = user_dict.pop('password')
    
    # Create user object without password field
    user = User(**user_dict)
    
    # Hash the password and set it on the user object
    user.hashed_password = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()).decode('utf-8')
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
    # return {
    #     "message":"User created successfully",
    #     "user_id": str(user.id)
    # }

async def update_user(db: AsyncSession, user_id: Union[str, uuid.UUID], user_data: UserUpdate) -> User:
    # Convert string to UUID if needed
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
        
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
    # return {
    #     "message":"User updated successfully",
    #     "user_id": str(user.id)
    # }

async def delete_user(db: AsyncSession, user_id: Union[str, uuid.UUID]):
    # Convert string to UUID if needed
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
        
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}

async def get_user_by_id(db: AsyncSession, user_id: Union[str, uuid.UUID]) -> User:
    """
    Get a user by their ID.
    
    Args:
        db: Database session
        user_id: ID of the user to retrieve
        
    Returns:
        User object if found, None otherwise
    """
    # Convert string to UUID if needed
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
        
    user = await db.get(User, user_id)
    return user

async def get_users(db: AsyncSession):
    """
    Get all users.
    
    Args:
        db: Database session
        
    Returns:
        List of all users
    """
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

async def get_all_user_courses(db: AsyncSession, user_id: uuid.UUID):
    """
    Get all Courses for a specificed user.
    
    Args:
        db: Database session
        user_id: user id of the faculty
        
    Returns:
        List of Courses with their details
    """
    logger.info(f"Fetching courses for user with ID: {user_id}")
    try:
        query = (
            select(Course, User.name)
            .join(CourseEnrollment, Course.id == CourseEnrollment.course_id)
            .join(User, Course.created_by == User.id)
            .where(CourseEnrollment.student_id == user_id)
            .distinct()
        )
        result = await db.execute(query)
        courses = result.all()
        # Check if the course is bookmarked by the user
        logger.info(f"Found {len(courses)} courses for user with ID: {user_id}")
        logger.info(f"Checking if the course is bookmarked for user")

        courses_data = []
        for course, faculty_name in courses:
            result = await db.execute(select(BookmarkedMaterials).where(BookmarkedMaterials.course_id == course.id))
            is_bookmarked = result.scalars().first() is not None  # Convert to boolean
            
            # Convert SQLAlchemy object to dictionary before adding extra fields
            course_dict = {**course.__dict__}  
            course_dict.pop("_sa_instance_state", None)  # Remove SQLAlchemy metadata
            course_dict["is_bookmarked"] = is_bookmarked
            course_dict["created_by"] = faculty_name  

            courses_data.append(course_dict)

        logger.info(f"Final course data prepared for user: {user_id}")
        return courses_data  # Return as JSON response

    except Exception as e:
        logger.error(f"Error fetching courses for user with error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



async def fetch_user_course_content(db: AsyncSession, course_id: uuid.UUID):
    """
    Get course content for a specified course.
    
    Args:
        db: Database session
        course_id: Course ID of the faculty
        
    Returns:
        Dictionary containing course content
    """
    try:
        # Fetch course with eager loading of modules and lectures
        query = (
            select(Course)
            .where(Course.id == course_id)
            .options(
                selectinload(Course.modules).selectinload(Module.lectures)
            )  # Eagerly load related data
        )
        result = await db.execute(query)
        course = result.scalars().first()

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Fetch instructor separately
        instructor_result = await db.execute(select(User).where(User.id == course.faculty_id))
        instructor = instructor_result.scalars().first()
        instructor_name = instructor.name if instructor else "Unknown"

        syllabus = []
        for module in course.modules:
            all_lectures = []
            for lecture in module.lectures:
                # Fetch lecture content eagerly instead of separate queries
                lecture_content_result = await db.execute(
                    select(LectureContent).where(LectureContent.lecture_id == lecture.id)
                )
                lecture_content = lecture_content_result.scalars().first()

                if lecture_content:  # Ensure lecture_content is not None
                    lecture_content_data = {
                        "id": lecture_content.id,
                        "title": lecture_content.title,
                        "type": lecture.content_type,
                        "videoUrl": lecture_content.content_url,
                        "description": lecture_content.content_desc,
                        "lecture_seq":lecture.position,
                        "week":module.position
                    }
                    all_lectures.append(lecture_content_data)

            syllabus.append({
                "id": module.id,
                "title": module.title,
                "lectures": all_lectures,
                "week":module.position
            })

        response_data = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "duration": course.duration,
            "lastUpdated": str(course.updated_at),  
            "instructor": {
                "name": instructor_name,
                "title": "Senior Python Developer & Educator",
            },
            "syllabus": syllabus,
        }
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
