from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import select
from app.models.course import Course, Module, LectureContent, Lecture, CourseEnrollment, LectureContentDoc
from fastapi import HTTPException
import uuid

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


