import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.future import select
from sqlalchemy import select, and_

from app.database import get_db
from app.services.auth_service import get_current_user
from app.schemas.enrollment import StudentInfo, StudentProgress
from app.models.course import Course, CourseEnrollment
from app.models.user import User
from pydantic import BaseModel

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/courses", tags=["enrollments"])

@router.get("/{course_id}/student", response_model=List[StudentInfo])
async def get_course_students(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all students enrolled in a specific course.
    Returns basic information about each student (id, name, email, avatar).
    """
    logger.info(f"Inside get_course_students funtion before try...course_id: {course_id}")
    try:
        # Check user permissions (must be faculty or admin)
        logger.info(f"Inside try in get_course_students...Going to check user role: {current_user.get('role')}")
        if current_user.get("role") not in ["faculty", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to view this information")
        
        # Check if course exists
        logger.info(f"Going to check if course exists: {course_id}")
        result = await db.execute(select(Course).where(Course.id == course_id))
        course = result.scalar_one_or_none()

        if course is None:
            raise HTTPException(status_code=404, detail=f"Course with ID {course_id} not found")

        # Get all enrolled students for this course
        logger.info(f"Going to get students for course: {course_id}")
        stmt = (
            select(User.id, User.name, User.email, User.picture, 
                CourseEnrollment.last_activity, CourseEnrollment.status)
            .join(CourseEnrollment, User.id == CourseEnrollment.student_id)
            .where(CourseEnrollment.course_id == course_id)
            .order_by(User.name)
        )
        
        result = await db.execute(stmt)
        students = [
            {
                "id": row.id,
                "name": row.name,
                "email": row.email,
                "avatar": row.picture,
                "last_activity": row.last_activity,
                "status": row.status
            }
            for row in result.all()
        ]
        logger.info("Data retrieved")
        return students
    except Exception as e:
        logger.error(f"Error retrieving students for course {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve students: {str(e)}")

@router.get("/{course_id}/progress", response_model=List[StudentProgress])
async def get_course_progress(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get progress data for students in a specific course.
    Returns progress percentage and assignment completion for each student.
    """
    try:
        # Check user permissions (must be faculty or admin)
        logger.info(f"Inside get_course_progress..Going to check user role: {current_user.get('role')}")
        if current_user.get("role") not in ["faculty", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to view this information")
        
        # Check if course exists
        logger.info(f"Going to check if course exists: {course_id}")
        query = text("""
            SELECT EXISTS(SELECT 1 FROM courses WHERE id = :course_id)
        """)
        exists = await db.execute(query, {"course_id": str(course_id)})
        if not exists.fetchone()[0]:
            raise HTTPException(status_code=404, detail=f"Course with ID {course_id} not found")

        # Get all students' progress for this course
        logger.info(f"Course exists...Going to get progress data for course: {course_id}")
        query = text("""
            WITH assignment_counts AS (
                SELECT 
                    COUNT(*) as total_assignments
                FROM 
                    assignments
                WHERE 
                    course_id = :course_id
            ),
            student_assignments AS (
                SELECT 
                    ce.student_id,
                    COUNT(s.id) as completed_assignments
                FROM 
                    course_enrollments ce
                LEFT JOIN 
                    submissions s ON ce.student_id = s.student_id
                LEFT JOIN 
                    assignments a ON s.assignment_id = a.id
                WHERE 
                    ce.course_id = :course_id
                    AND a.course_id = :course_id
                    AND s.status = 'completed'
                GROUP BY 
                    ce.student_id
            )
            SELECT 
                ce.student_id,
                ce.status,
                ce.last_activity as last_activity,
                COALESCE(sa.completed_assignments, 0) as completed_assignments,
                COALESCE(ac.total_assignments, 0) as total_assignments
            FROM 
                course_enrollments ce
            CROSS JOIN 
                assignment_counts ac
            LEFT JOIN 
                student_assignments sa ON ce.student_id = sa.student_id
            WHERE 
                ce.course_id = :course_id
        """)
        result = await db.execute(query, {"course_id": str(course_id)}) ##ce.progress,
        progress_data = []
        
        for row in result.fetchall():
            progress = {
                "student_id": row[0],
                "progress": row[1] or 0,  # Default to 0 if None
                "last_activity": row[2],
                "completed_assignments": row[3],
                "total_assignments": row[4]
            }
            progress_data.append(progress)
            
        return progress_data
        
    except Exception as e:
        logger.error(f"Error retrieving progress data for course {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve progress data: {str(e)}")

@router.get("/{course_id}/enrollments", response_model=List[Dict])
async def get_course_enrollments(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all enrollments for a specific course.
    Returns detailed information about each enrollment.
    """
    try:
        # Check user permissions (must be faculty or admin)
        if current_user.get("role") not in ["faculty", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to view this information")
        
        # Get all enrollments for this course with user info
        query = """
            SELECT 
                ce.id, 
                ce.student_id,
                u.name,
                u.email,
                u.picture,
                ce.status,
                ce.enrollment_date,
                ce.status,
                ce.last_activity,
                ce.grade,
                ce.completion_date
            FROM 
                course_enrollments ce
            JOIN 
                users u ON ce.student_id = u.id
            WHERE 
                ce.course_id = :course_id
            ORDER BY 
                u.name
        """
        result = await db.execute(query, {"course_id": str(course_id)})
        enrollments = []
        
        for row in await result.fetchall():
            enrollment = {
                "id": row[0],
                "student_id": row[1],
                "name": row[2],
                "email": row[3],
                "picture": row[4],
                "status": row[5],
                "enrollment_date": row[6],
                "progress": row[7],
                "last_activity": row[8],
                "grade": row[9],
                "completion_date": row[10]
            }
            enrollments.append(enrollment)
            
        return enrollments
        
    except Exception as e:
        logger.error(f"Error retrieving enrollments for course {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve enrollments: {str(e)}")

@router.get("/{course_id}/enrollments/{enrollment_id}", response_model=Dict)
async def get_enrollment_details(
    course_id: UUID,
    enrollment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific enrollment.
    Returns enrollment details including assignment completion data.
    """
    try:
        # Check user permissions (must be faculty or admin)
        if current_user.get("role") not in ["faculty", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to view this information")
        
        # Get enrollment details
        query = """
            SELECT 
                ce.id, 
                ce.student_id,
                u.name,
                u.email,
                u.picture,
                ce.status,
                ce.enrollment_date,
                ce.progress,
                ce.last_activity,
                ce.grade,
                ce.completion_date,
                ce.certificate_url,
                ce.is_favorited
            FROM 
                course_enrollments ce
            JOIN 
                users u ON ce.student_id = u.id
            WHERE 
                ce.id = :enrollment_id
                AND ce.course_id = :course_id
        """
        result = await db.execute(query, {
            "enrollment_id": str(enrollment_id),
            "course_id": str(course_id)
        })
        
        row = await result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Enrollment with ID {enrollment_id} not found")
        
        enrollment = {
            "id": row[0],
            "student_id": row[1],
            "name": row[2],
            "email": row[3],
            "picture": row[4],
            "status": row[5],
            "enrollment_date": row[6],
            "progress": row[7],
            "last_activity": row[8],
            "grade": row[9],
            "completion_date": row[10],
            "certificate_url": row[11],
            "is_favorited": row[12],
            "assignments": []
        }
        
        # Get assignment completion data
        query = """
            SELECT 
                a.id,
                a.title,
                s.submitted_at,
                s.status,
                s.grade,
                s.graded_at
            FROM 
                assignments a
            LEFT JOIN 
                submissions s ON a.id = s.assignment_id AND s.student_id = :student_id
            WHERE 
                a.course_id = :course_id
            ORDER BY 
                a.due_date
        """
        result = await db.execute(query, {
            "student_id": str(enrollment["student_id"]),
            "course_id": str(course_id)
        })
        
        assignments = []
        for row in await result.fetchall():
            assignment = {
                "id": row[0],
                "title": row[1],
                "submitted_at": row[2],
                "status": row[3],
                "grade": row[4],
                "graded_at": row[5]
            }
            assignments.append(assignment)
        
        enrollment["assignments"] = assignments
        
        return enrollment
    except HTTPException as e:
        logger.error(f"Failed to retrieve enrollment details: {str(e)}")
        raise e
        
    except Exception as e:
        logger.error(f"Error retrieving enrollment details for {enrollment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve enrollment details: {str(e)}") 

class EnrollmentRequest(BaseModel):
    course_id: UUID  # UUID as a string
    student_emails: List[str]
    
@router.post("/enroll", response_model=Dict)
async def enroll_students_to_course(
    enrollment_data: EnrollmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Enroll multiple students in a course.
    Expects a list of student emails and a course ID.
    """
    try:
        logger.info(f"Received enrollment request: {enrollment_data}")

        # Check user permissions (must be faculty or admin)
        if current_user.get("role") not in ["faculty", "admin"]:
            logger.warning(f"Unauthorized enrollment attempt by user: {current_user}")
            raise HTTPException(status_code=403, detail="Not authorized to perform this action")

        course_id = enrollment_data.course_id
        student_emails = enrollment_data.student_emails
        logger.info(f"Enrolling students: {student_emails} into course: {course_id}")

        # Check if course exists
        course = await db.execute(select(Course).where(Course.id == course_id))
        course = course.scalar_one_or_none()
        if not course:
            logger.error(f"Course not found: {course_id}")
            raise HTTPException(status_code=404, detail=f"Course with ID {course_id} not found")

        logger.info(f"Course found: {course_id}. Fetching student details...")

        # Get students by email
        result = await db.execute(select(User).where(User.email.in_(student_emails)))
        students = result.scalars().all()

        if not students:
            logger.warning("No valid students found for enrollment.")
            raise HTTPException(status_code=404, detail="No valid students found for enrollment")

        logger.info(f"Found {len(students)} students. Checking for existing enrollments...")

        # Prepare enrollments
        enrollments = []
        for student in students:
            existing_enrollment = await db.execute(
            select(CourseEnrollment)
            .where(
                and_(
                    CourseEnrollment.student_id == student.id, 
                    CourseEnrollment.course_id == course_id
                    )
                )
            )
            if existing_enrollment.scalar_one_or_none() is None:  # Avoid duplicates
                logger.info(f"Enrolling student {student.email} (ID: {student.id}) into course {course_id}")
                enrollment_obj = CourseEnrollment(
                    course_id=course_id,
                    student_id=student.id, 
                    user_id=current_user.get("id")
                    #other fields are by default set in db
                    )
                enrollments.append(enrollment_obj)
            else:
                logger.info(f"Skipping student {student.email} (ID: {student.id}): Already enrolled")

        # Bulk insert enrollments
        if enrollments:
            db.add_all(enrollments)
            await db.commit()
            logger.info(f"Successfully enrolled {len(enrollments)} students into course {course_id}")
        else:
            logger.info("No new students were enrolled (all were already enrolled).")

        return {"message": f"Enrolled {len(enrollments)} students in the course"}

    except HTTPException as e:
        await db.rollback()
        logger.error(f"Failed to enroll students: {str(e)}")
        raise e

    except Exception as e:
        await db.rollback()
        logger.error(f"Error enrolling students: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to enroll students: {str(e)}")

@router.delete("/{course_id}/student/{student_id}", response_model=Dict)
async def remove_student_from_course(
    course_id: UUID,
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Remove a student from a course.
    """
    try:
        # Check user permissions (must be faculty or admin)
        if current_user.get("role") not in ["faculty", "admin"]:
            logger.warning(f"Unauthorized removal attempt by user: {current_user}")
            raise HTTPException(status_code=403, detail="Not authorized to perform this action")

        # Check if course exists
        course = await db.execute(select(Course).where(Course.id == course_id))
        course = course.scalar_one_or_none()
        if not course:
            logger.error(f"Course not found: {course_id}")
            raise HTTPException(status_code=404, detail=f"Course with ID {course_id} not found")

        # Check if student is enrolled
        enrollment = await db.execute(
            select(CourseEnrollment)
            .where(
                and_(
                    CourseEnrollment.student_id == student_id, 
                    CourseEnrollment.course_id == course_id
                    )
                )
            )
        enrollment = enrollment.scalar_one_or_none()
        if not enrollment:
            logger.error(f"Student {student_id} is not enrolled in course {course_id}")
            raise HTTPException(status_code=404, detail=f"Student is not enrolled in this course")

        # Remove student from course
        logger.info(f"Removing student {student_id} from course {course_id}")
        db.delete(enrollment)
        await db.commit()
        logger.info(f"Successfully removed student {student_id} from course {course_id}")
        
        check = await db.execute(
        select(CourseEnrollment).where(
            and_(
                    CourseEnrollment.student_id == student_id, 
                    CourseEnrollment.course_id == course_id
                    )
                )
        )
        remaining = check.scalars().first()
        logger.info(f"Remaining enrollment after delete: {remaining}")  # Should be None
        return {"message": "Student removed from course"}

    except HTTPException as e:
        await db.rollback()
        logger.error(f"Failed to remove student from course: {str(e)}")
        raise e

    except Exception as e:
        await db.rollback()
        logger.error(f"Error removing student from course: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to remove student from course: {str(e)}")