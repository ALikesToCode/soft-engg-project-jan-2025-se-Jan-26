from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import select, and_, String
from app.models.course import Course, Module, LectureContent, \
    Lecture, CourseEnrollment, LectureContentDoc, UserRecommendedCourses, BookmarkedMaterials
from app.models.assignment import Assignment
from app.models.user import User
from app.database import get_db
from fastapi import HTTPException, UploadFile, Form, File, Depends
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import and_
from app.utils.content_type import ContentType
import datetime
from app.models.course import CourseStatus
from uuid import UUID
from typing import List, Dict, Any
import os
import json
import shutil
import uuid
import enum
import logging
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import cast
from sqlalchemy.sql.functions import func
from datetime import UTC

logger = logging.getLogger(__name__)

class EnrollmentStatus(str, enum.Enum):
    ENROLLED = "enrolled"
    COMPLETED = "completed"
    DROPPED = "dropped"
    WAITLISTED = "waitlisted"


async def get_new_course_code(db: AsyncSession, user_id: uuid.UUID):
    """
    Get unique course code    
    Args:
        db: Database session
        user_id: user id of the faculty (optional)
    Returns:
        Unique course code
    """
    try:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user.role.lower() not in ['faculty']:
            raise HTTPException(status_code=403, detail="You are forbidden to use the resource")
        
        # Fetch existing course codes
        result = await db.execute(select(Course))
        course_codes = [course.code for course in result.scalars().all() if course.code.startswith("COURSE")]

        # Extract numeric part and find the highest number
        course_numbers = [
            int(code.replace("COURSE", "")) for code in course_codes if code.replace("COURSE", "").isdigit()
        ]

        next_number = max(course_numbers, default=100) + 1  # Start from COURSE101 if no courses exist

        new_course_code = f"COURSE{next_number}"

        return new_course_code

    except Exception as e:
        logger.error(f"Error generating course code: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating course code")


# Course Content Management Functions
async def get_all_courses(db: AsyncSession, user_id: uuid.UUID = None):
    """
    Get all Courses for a specific faculty user or all courses if no user_id is provided.
    
    Args:
        db: Database session
        user_id: user id of the faculty (optional)
        
    Returns:
        List of Courses with their details
    """
    try:
        logger.info("Inside get_all_courses function in course_service")
        if user_id:
            # Fetch all course objects for a specific faculty
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalars().first()
            if(user.role == 'support'):
                result = await db.execute(
                select(Course)
            )
            else:
                result = await db.execute(
                    select(Course).where(Course.faculty_id == user_id)
                )
        else:
            # Fetch all course objects
            result = await db.execute(select(Course))
        logger.info("Courses fetched successfully...")
        courses = result.scalars().all()
        return [course.to_dict() for course in courses]
    except Exception as e:
        logger.error(f"Error fetching courses: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching courses")

async def get_modules_by_course(course_id: str, db: AsyncSession, user_id: uuid.UUID):
    """
    Get all Modules for the given course id.
        
    Args:
        course_id: course id of the course
        db: Database session
        user_id: user id of the faculty
            
    Returns:
        List of Modules with their details
    """
    # Fetch the course object and raise error if not found
    course = await db.execute(select(Course).where(Course.id == course_id))
    course = course.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    #check if the faculty is created the course and raise error if not
    faculty_id = UUID(str(course.faculty_id))
    user_id_uuid = UUID(str(user_id))
    if faculty_id != user_id_uuid:
        logger.info(f"You are not the faculty of the course faculty_id={course.faculty_id} user_id={user_id}")
        raise HTTPException(status_code=403, detail="You are not authorized to view this course")
    
    # Fetch all modules for the given course and return as a list
    result = await db.execute(
        select(Module).where(Module.course_id == course_id).order_by(Module.position)
    )
    modules = result.scalars().all()  
    return [module.to_dict() for module in modules]

async def get_lecture_for_module(module_id: int, db: AsyncSession, user_id: uuid.UUID):
    """
    Get Lecture for the given module.
        
    Args:
        module_id: module id of the module
        db: Database session
        user_id: user id of the faculty
            
    Returns:
        List of Lectures with their details
    """    
    try:
        # Fetch the module object and raise error if not found
        module = await db.execute(select(Module).where(Module.id == module_id))
        module = module.scalars().first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        #Fetch all lectures for the given module and return as a list
        result = await db.execute(select(Lecture).where(Lecture.module_id == module_id))
        lectures = result.scalars().all()  
        return [lecture.to_dict() for lecture in lectures]
    except Exception as e:
        logger.error(f"Error fetching lectures: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_lecture_content_by_module(module_id: int, db: AsyncSession, user_id: uuid.UUID):
    """
    Get Lecture Content for the given module.
        
    Args:
        module_id: module id of the module
        db: Database session
        user_id: user id of the faculty
            
    Returns:
        List of Lecture Contents with their details
    """

    # Fetch all lectures for the given module
    result = await db.execute(
        select(Lecture)
        .options(joinedload(Lecture.contents))
        .where(Lecture.module_id == module_id)
    )

    # Check if lectures exist
    lectures = result.scalars().unique().all() 
    if not lectures:
        raise HTTPException(status_code=404, detail="No lectures found for the given module")

    # Flatten contents from lectures and return as a list
    contents = [content for lecture in lectures for content in lecture.contents]
    return [content.to_dict() for content in contents]

async def get_lecture_content_by_lecture(lecture_id: int, db: AsyncSession, user_id: uuid.UUID):
    """
    Get Lecture Content for the given lecture.
        
    Args:
        lecture_id: lecture id of the lecture
        db: Database session
        user_id: user id of the faculty
            
    Returns:
        Lecture Content for the given lecture
    """
    logger.info("Inside get_lecture_content_by_lecture in course_service")
    try:
        # Fetch the lecture content for the given lecture
        result = await db.execute(select(LectureContent).where(LectureContent.lecture_id == lecture_id))
        content = result.scalars().first() 
        if not content:
            logger.info("Checking for video content")
            #If the video content is not found, check for document content
            result = await db.execute(select(LectureContentDoc).where(LectureContentDoc.lecture_id == lecture_id))
            content = result.scalars().first()

            #Raise error if no content found
            if not content:
                logger.info("Video content Not found...Checking for doc content")
                raise HTTPException(status_code=404, detail="No content found for the given lecture")
        #if content is found, return the content
        return content.to_dict()
    except Exception as e:
        logger.error(f"Error fetching course content: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def add_new_course(course_data, db: AsyncSession, user_id: uuid.UUID):
    """
    Add a new course to the database.
        
    Args:
        course_data: Course data to be added
        db: Database session
        user_id: user id of the faculty
            
    Returns:
        Newly added course
    """
    try:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user.role.lower() not in ['faculty']:
            raise HTTPException(status_code=403, detail="You are forbidden to use the resource")
        
        # Create a new course object and add to the database
        new_course = Course(
            name=course_data.name,
            code=course_data.code,
            title=course_data.title,
            credits=course_data.credits,
            duration=course_data.duration,
            semester=course_data.semester,
            year=course_data.year,
            faculty_id=user_id,
            created_by=user_id,
            syllabus=course_data.syllabus,
            description=course_data.description,
            start_date=course_data.start_date,
            end_date=course_data.end_date,
            level=course_data.level,
        )
        db.add(new_course)
        await db.commit()
        await db.refresh(new_course)
        return new_course
    except Exception as e:
        await db.rollback()
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def add_lecture_content_to_existing_course(content,db: AsyncSession, user_id: uuid.UUID):
    """
    Add Lecture Content to an existing course.
        
    Args:
        content: Content data to be added
        db: Database session
        user_id: user id of the faculty
            
    Returns:
        Lecture Content added to the course
    """
    try:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user.role.lower() not in ['faculty']:
            raise HTTPException(status_code=403, detail="You are forbidden to use the resource")

        # Check if course exists and raise error if not found
        course = await db.execute(select(Course).where(Course.id == content.courseId))
        course = course.scalars().first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Check if module exists and raise error if not found
        module = await db.execute(select(Module).where(Module.id == int(content.moduleId)))
        module = module.scalars().first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Query to fetch the last lecture for the given module
        lectures = await db.execute(
            select(Lecture)
            .where(and_(Lecture.module_id == int(content.moduleId), Lecture.content_type == 'lecture'))
            .order_by(Lecture.position.desc())  # Sorting in descending order
            .limit(1)  # Fetch only the top row
        )
        first_lecture = lectures.scalars().first()

        # Calculate the position for the new lecture content
        position = 1 if not first_lecture else first_lecture.position + 1

        content_type = "lecture"
        if(content.type == "quiz"):
            content_type = ContentType.QUIZ
        elif(content.type == "assignment"):
            content_type = ContentType.ASSIGNMENT
        elif(content.type == "document"):
            content_type = ContentType.DOCUMENT

        # Create a new lecture object and add to the database
        new_lecture = Lecture(
            module_id=int(content.moduleId),
            content_type='lecture',
            position=position,
        )
        db.add(new_lecture)
        await db.commit()
        await db.refresh(new_lecture)

        # Create a new lecture content object and add to the database
        new_lecture_content = LectureContent(
            lecture_id=new_lecture.id,
            title=content.title,
            content_url=content.videoUrl,
            content_desc=content.description,
        )
        db.add(new_lecture_content)
        await db.commit()
        await db.refresh(new_lecture_content)

        # Return the newly added lecture content
        return new_lecture_content.to_dict()
    
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        await db.rollback()  # Rollback if error occurs
        raise HTTPException(status_code=500, detail=str(e))



async def add_doc_content_to_existing_course(content,db: AsyncSession, user_id: uuid.UUID):
    """
    Add document lecture Content (pdf/ppt) to an existing course.
        
    Args:
        content: Content data to be added
        db: Database session
        user_id: user id of the faculty
            
    Returns:
        Lecture Content added to the course
    """
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()
    if user.role.lower() not in ['faculty']:
        raise HTTPException(status_code=403, detail="You are forbidden to use the resource")

    try:
        # Check if course exists and raise error if not found
        course = await db.execute(select(Course).where(Course.id == content.courseId))
        course = course.scalars().first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if the faculty has created the course and raise error if not
        if course.faculty_id != user_id:
            raise HTTPException(status_code=403, detail="You are not authorized to add content to this course")

        # Check if module exists and raise error if not found
        module = await db.execute(select(Module).where(Module.id == int(content.moduleId)))
        module = module.scalars().first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Query to fetch the last lecture for the given module
        lectures = await db.execute(
            select(Lecture)
            .where(and_(Lecture.module_id == int(content.moduleId), Lecture.content_type == 'document'))
            .order_by(Lecture.position.desc())  # Sorting in descending order
            .limit(1)  # Fetch only the top row
        )
        first_lecture = lectures.scalars().first()

        # Calculate the position for the new lecture content
        position = 1 if not first_lecture else first_lecture.position + 1

        # Create a new lecture object and add to the database
        new_lecture = Lecture(
            module_id=int(content.moduleId),
            content_type='document',
            position=position,
        )
        db.add(new_lecture)
        await db.commit()
        await db.refresh(new_lecture)

        # Create a new lecture content object and add to the database
        new_lecture_content = LectureContentDoc(
            lecture_id=new_lecture.id,
            title=content.title,
            content_doc=str(content.driveDocLink),
            content_desc=content.description,
            file_type=content.type,
        )
        db.add(new_lecture_content)
        await db.commit()
        await db.refresh(new_lecture_content)
        return new_lecture_content.to_dict()
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        await db.rollback()  # Rollback if error occurs
        raise HTTPException(status_code=500, detail=str(e))


async def update_existing_lecture_doc_content(content,db: AsyncSession, user_id: uuid.UUID):
    """
    Update Document Lecture Content(pdf/ppt) to an existing course.
        
    Args:
        content: Content data to be added
        db: Database session
        user_id: user id of the faculty
            
    Returns:
        Updated Lecture Content
    """
    try:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user.role.lower() not in ['faculty']:
            raise HTTPException(status_code=403, detail="You are forbidden to use the resource")

        # Check if course exists and raise error if not found
        course = await db.execute(select(Course).where(Course.id == content.courseId))
        course = course.scalars().first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if the faculty has created the course and raise error if not
        if course.faculty_id != user_id:
            raise HTTPException(status_code=403, detail="You are not authorized to add content to this course")
        
        # Check if lecture exists and raise error if not found
        lecture_id = int(content.lectureId)
        result = await db.execute(
        select(Lecture)
        .join(LectureContentDoc, Lecture.id == LectureContentDoc.lecture_id)
        .where(LectureContentDoc.id == lecture_id)
        )
        lecture = result.scalars().first()
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        # Check if the lecture content type is getting modified and raise error if so
        if lecture.content_type != content.type:
            raise HTTPException(status_code=400, detail="Content type cannot be changed")

        # Check if LectureContent exists 
        lecture_content = await db.execute(select(LectureContentDoc).where(LectureContentDoc.id == int(lecture_id)))
        lecture_content = lecture_content.scalars().first()
        if not lecture_content:
            raise HTTPException(status_code=404, detail="LectureContent not found")
        
        # update the content 
        try:
            lecture_content.title = content.title
            lecture_content.content_doc = str(content.driveDocLink)
            lecture_content.content_desc = content.description
            await db.commit()
            return lecture_content.to_dict()
        except Exception as e:
            await db.rollback()  
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        await db.rollback() 
        raise HTTPException(status_code=500, detail=str(e))

async def update_existing_lecture_content(content,db: AsyncSession, user_id: uuid.UUID):
    """
    Update Video Lecture Content to an existing course.
        
    Args:
        content: Content data to be added
        db: Database session
        user_id: user id of the faculty
            
    Returns:
        Updated Lecture Content
    """
    try:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user.role.lower() not in ['faculty']:
            raise HTTPException(status_code=403, detail="You are forbidden to use the resource")

        lecture_id = int(content.lectureId)
        # Check if the lecture exists and raise error if not found
        result = await db.execute(
        select(Lecture)
        .join(LectureContent, Lecture.id == LectureContent.lecture_id)
        .where(LectureContent.id == lecture_id)
        )
        lecture = result.scalars().first()
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        # Check if the lecture content type is getting modified and raise error if so
        if lecture.content_type != content.type:
            raise HTTPException(status_code=400, detail="Content type cannot be changed")

        # Check if LectureContent exists and raise error if not found
        lecture_content = await db.execute(select(LectureContent).where(LectureContent.id == int(lecture_id)))
        lecture_content = lecture_content.scalars().first()
        if not lecture_content:
            raise HTTPException(status_code=404, detail="LectureContent not found")
        
        # update the content
        try:
            lecture_content.title = content.title
            lecture_content.content_url = content.videoUrl
            lecture_content.content_desc = content.description
            await db.commit()
            return lecture_content.to_dict()
        except Exception as e:
            await db.rollback()  
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        await db.rollback()  # Rollback if error occurs
        raise HTTPException(status_code=500, detail=str(e))

async def add_module(module_data, db: AsyncSession, user_id: uuid.UUID):
    """
    Add Module to an existing course.
        
    Args:
        module_data: Module data to be added
        db: Database session
        user_id: user id of the faculty
            
    Returns:
        Newly added Module
    """
    try:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user.role.lower() not in ['faculty']:
            raise HTTPException(status_code=403, detail="You are forbidden to use the resource")

        # Check if course exists and raise error if not found
        course = await db.execute(select(Course).where(Course.id == module_data.course_id))
        course = course.scalars().first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if the faculty has created the course and raise error if not
        faculty_id = UUID(str(course.faculty_id))
        user_id_uuid = UUID(str(user_id))
        if faculty_id != user_id_uuid:
            raise HTTPException(status_code=403, detail="You are not authorized to add modules to this course")

        # Create a new module object and add to the database
        new_module = Module(
            course_id=module_data.course_id,
            title=module_data.title,
            position=module_data.position,
        )
        db.add(new_module)
        await db.commit()
        await db.refresh(new_module)
        return new_module
    except Exception as e:
        await db.rollback()
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def delete_module_by_id(module_id: int, db: AsyncSession, user_id: uuid.UUID):
    """
    Deletes Module by id.
        
    Args:
        module_id: id of the module to be deleted
        db: Database session
        user_id: user id of the faculty
            
    Returns:
        String message indicating the deletion status
    """
    try:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user.role.lower() not in ['faculty']:
            raise HTTPException(status_code=403, detail="You are forbidden to user the resource")

        # Fetch the module object and raise error if not found
        result = await db.execute(select(Module).filter(Module.id == module_id))
        module = result.scalars().first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Delete the module and commit the transaction
        await db.delete(module)
        await db.commit()
        return {"message": "Module deleted successfully"}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import cast
# Course Service Class for Enrollment and Assignment Management
class CourseService:
    @staticmethod
    async def get_user_course_history(db: AsyncSession, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Get the course history for a specific user.
        
        Args:
            db: Database session
            user_id: UUID of the user
            
        Returns:
            List of courses with their details
        """
        query = (
            select(Course, CourseEnrollment)
            .join(CourseEnrollment, Course.id == CourseEnrollment.course_id)
            .where(CourseEnrollment.student_id == user_id)
        )
        result = await db.execute(query)
        courses = []

        total_course_count = 0
        for course, enrollment in result:
            total_course_count += 1
            # Get instructor info
            instructor_data = await db.execute(select(User).where(User.id==course.faculty_id))
            instructor = instructor_data.scalars().first()
            instructor_name = instructor.name if instructor else "Unknown"
            
            courses.append({
                "id": str(course.id),
                "name": course.name,
                "code": course.code,
                "semester": course.semester,
                "status": enrollment.status,
                "grade": enrollment.grade,
                "credits": course.credits,
                "instructor": instructor_name,
                "description": course.description,
                "completion_date": enrollment.completion_date,
                "certificate_url": enrollment.certificate_url,
                "enrollment_date": enrollment.enrollment_date,
                "progress": enrollment.progress,
                "last_activity": enrollment.last_activity
            })
        
        # Add the total count to all courses
        for course in courses:
            course["total_enrolled_course"] = total_course_count
        
        return courses

    @staticmethod
    async def get_course_enrollment(db: AsyncSession, course_id: UUID) -> List[Dict[str, Any]]:
        """
        Get the enrollment list for a specific course.
        
        Args:
            db: Database session
            course_id: UUID of the course
            
        Returns:
            List of enrolled students with their details
        """
        query = (
            select(User, CourseEnrollment)
            .join(CourseEnrollment, User.id == CourseEnrollment.student_id)
            .where(CourseEnrollment.course_id == course_id)
        )
        
        result = await db.execute(query)
        enrollment = []
        
        for user, enrollment_record in result:
            enrollment.append({
                "student_id": str(user.id),
                "name": user.name,
                "email": user.email,
                "enrollment_date": enrollment_record.enrollment_date.isoformat(),
                "status": enrollment_record.status
            })
        
        return enrollment

    @staticmethod
    async def get_all_course_assignments(db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Get all assignments across all courses.
        
        Args:
            db: Database session
            
        Returns:
            List of assignments with their details
        """
        try:
            # Get all assignments with their corresponding courses
            query = (
                select(Assignment, Course)
                .outerjoin(Course, Assignment.course_id == Course.id)
            )
            
            result = await db.execute(query)
            assignments = []
            
            rows = result.fetchall()
            if not rows:
                return []  # Return empty list if no assignments exist
            
            for assignment, course in rows:
                if assignment:  # Only add if we have an assignment
                    assignment_data = {
                        "id": str(assignment.id),
                        "course_id": str(course.id) if course else None,
                        "course_name": course.name if course else "Unknown Course",
                        "title": assignment.title,
                        "description": assignment.description,
                        "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
                        "status": assignment.status,
                        "points": assignment.points,
                        "submission_type": assignment.submission_type,
                        "allow_late_submissions": assignment.allow_late_submissions,
                        "file_types": assignment.file_types
                    }
                    assignments.append(assignment_data)
            
            return assignments
        except Exception as e:
            print(f"Error in get_all_course_assignments: {str(e)}")  # Log the error
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to retrieve course assignments: {str(e)}"
            )
        
    async def get_user_recommended_courses(db: AsyncSession, user_id: UUID):
        try:
            # Validate if the user exists
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalars().first()
            if not user:
                logger.warning(f"User with ID {user_id} not found when fetching recommended courses")
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get recommended courses
            result = await db.execute(select(UserRecommendedCourses).where(UserRecommendedCourses.user_id == user_id))
            recommended_courses = result.scalars().all()
            return [rc.to_dict() for rc in recommended_courses]
        except HTTPException as http_ex:
            # Re-raise HTTP exceptions
            raise http_ex
        except Exception as e:
            logger.error(f"Error getting recommended courses for user {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve recommended courses: {str(e)}")
    
    async def get_user_bookmarked_materials(db: AsyncSession, user_id: UUID):
        try:
            # Validate if the user exists
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalars().first()
            if not user:
                logger.warning(f"User with ID {user_id} not found when fetching bookmarked materials")
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get bookmarked materials
            result = await db.execute(select(BookmarkedMaterials).where(BookmarkedMaterials.user_id == user_id))
            bookmarked_materials = result.scalars().all()
            return [bm.to_dict() for bm in bookmarked_materials]
        except HTTPException as http_ex:
            # Re-raise HTTP exceptions
            raise http_ex
        except Exception as e:
            logger.error(f"Error getting bookmarked materials for user {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve bookmarked materials: {str(e)}")
    
    async def add_user_bookmarked_materials(bookmark_data,db, user_id):
        try:
            # Validate if the user exists
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if user is None:
                logger.warning(f"User with ID {user_id} not found when adding bookmarked material")
                raise HTTPException(status_code=404, detail="User not found")
            
            # Validate if the course exists
            if bookmark_data.course_id:
                course_result = await db.execute(select(Course).where(Course.id == bookmark_data.course_id))
                course = course_result.scalars().first()
                if not course:
                    logger.warning(f"Course with ID {bookmark_data.course_id} not found when adding bookmark")
                    raise HTTPException(status_code=404, detail="Course not found")
            
            # Check if bookmark already exists
            existing_bookmark = await db.execute(
                select(BookmarkedMaterials).where(
                    and_(
                        BookmarkedMaterials.user_id == user_id,
                        BookmarkedMaterials.course_id == bookmark_data.course_id,
                        BookmarkedMaterials.title == bookmark_data.title,
                        BookmarkedMaterials.type == bookmark_data.type
                    )
                )
            )
            if existing_bookmark.scalars().first():
                logger.info(f"Material already bookmarked by user {user_id}")
                raise HTTPException(status_code=400, detail="Material already bookmarked")
            
            # Create a new bookmark object and add to the database
            new_bookmark = BookmarkedMaterials(
                user_id=user_id,
                title=bookmark_data.title,
                type=bookmark_data.type,
                date_bookmarked=datetime.datetime.utcnow(),
                author=bookmark_data.author,
                course_id=bookmark_data.course_id,
            )
            db.add(new_bookmark)
            await db.commit()
            await db.refresh(new_bookmark)
            logger.info(f"Added bookmark for user {user_id}: {bookmark_data.title}")
            return new_bookmark.to_dict()
        except HTTPException as http_ex:
            await db.rollback()
            raise http_ex
        except Exception as e:
            await db.rollback()
            logger.error(f"Error while saving bookmark: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save bookmark: {str(e)}")

    async def delete_bookmarked_material(db: AsyncSession, user_id: UUID, bookmark_id: int):
        try:
            # Validate if the user exists
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalars().first()
            if not user:
                logger.warning(f"User with ID {user_id} not found when deleting bookmark")
                raise HTTPException(status_code=404, detail="User not found")
            
            # Find the bookmark to delete
            result = await db.execute(
                select(BookmarkedMaterials).where(
                    and_(
                        BookmarkedMaterials.id == bookmark_id,
                        BookmarkedMaterials.user_id == user_id
                    )
                )
            )
            bookmark = result.scalars().first()
            if not bookmark:
                logger.warning(f"Bookmark with ID {bookmark_id} not found for user {user_id}")
                raise HTTPException(status_code=404, detail="Bookmark not found")

            # Delete the bookmark
            await db.delete(bookmark)
            await db.commit()
            logger.info(f"Deleted bookmark ID {bookmark_id} for user {user_id}")

            # Return updated list of bookmarked materials
            result = await db.execute(select(BookmarkedMaterials).where(BookmarkedMaterials.user_id == user_id))
            bookmarked_materials = result.scalars().all()
            return [bm.to_dict() for bm in bookmarked_materials]
        except HTTPException as http_ex:
            await db.rollback()
            raise http_ex
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting bookmark {bookmark_id} for user {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete bookmark: {str(e)}")

async def get_students_by_course(course_id: UUID, db: AsyncSession):
    """
    Get all students enrolled in a specific course.
    
    Args:
        course_id: UUID of the course
        db: Database session
        
    Returns:
        List of student dictionaries with their details
    """
    try:            
        # Fetch all students for the given course and return as a list
        result = await db.execute(
            select(User).join(CourseEnrollment, CourseEnrollment.student_id == User.id).where(
                CourseEnrollment.course_id == course_id
            )
        )
        students = result.scalars().all()
        all_students = []
        for student in students:
            all_students.append({
                "id": str(student.id),
                "name": student.name,
                "email": student.email,
                "picture": student.picture,
            })
        return all_students
    except Exception as e:
        logger.error(f"Error fetching students for course {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching students")