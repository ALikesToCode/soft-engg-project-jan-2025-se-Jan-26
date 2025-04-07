import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from enum import Enum
from pydantic import BaseModel

from app.database import get_db
from app.services.auth_service import get_current_user
from app.schemas.enrollment import StudentInfo, StudentProgress
from app.models.course import Course, CourseEnrollment
from app.models.user import User

# Define the Role enum locally since it's missing
class Role(str, Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    SUPPORT = "support"
    ADMIN = "admin"
    SUPERUSER = "superuser"

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/courses", tags=["enrollments"])

# Define common permission roles for reuse
STAFF_ROLES = [Role.FACULTY.value, Role.SUPPORT.value, Role.ADMIN.value, Role.SUPERUSER.value]
ADMIN_ROLES = [Role.FACULTY.value, Role.ADMIN.value, Role.SUPERUSER.value]

async def validate_course_exists(course_id: UUID, db: AsyncSession) -> bool:
    """Validate that a course exists in the database using SQLAlchemy ORM."""
    result = await db.execute(select(Course).where(Course.id == course_id))
    return result.scalar_one_or_none() is not None

async def check_user_permissions(current_user: Dict[str, Any], required_roles: List[str], 
                                course_id: Optional[UUID] = None, 
                                student_id: Optional[str] = None,
                                db: Optional[AsyncSession] = None) -> None:
    """Check if user has the required permissions."""
    user_role = current_user.get("role")
    
    # If user's role is in the required roles, they have permission
    if user_role in required_roles:
        return
    
    # Special case: students can access their own data
    if (user_role == Role.STUDENT.value and 
        student_id and current_user.get("id") == student_id):
        return
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to access this resource"
    )

@router.get("/{course_id}/students", response_model=List[StudentInfo])
async def get_course_students(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Retrieve all students enrolled in a specific course.
    Only faculty teaching the course, support staff, or superusers can access this endpoint.
    """
    # Check permissions
    await check_user_permissions(current_user, STAFF_ROLES)
    
    try:
        # Check if course exists using SQLAlchemy ORM
        if not await validate_course_exists(course_id, db):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
            
        # Get all students for this course using SQLAlchemy ORM
        stmt = (
            select(User.id, User.name, User.email, User.picture.label("avatar"), 
                CourseEnrollment.enrollment_date, CourseEnrollment.status)
            .join(CourseEnrollment, User.id == CourseEnrollment.student_id)
            .where(CourseEnrollment.course_id == course_id)
            .order_by(User.name)
        )
        
        result = await db.execute(stmt)
        students = [
            StudentInfo(
                id=row.id,
                name=row.name,
                email=row.email,
                avatar=row.avatar,
                enrollment_date=row.enrollment_date,
                status=row.status
            )
            for row in result.all()
        ]
        
        return students
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_course_students: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching students: {str(e)}"
        )

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
        # Check permissions
        await check_user_permissions(current_user, ADMIN_ROLES)
        
        # Check if course exists
        if not await validate_course_exists(course_id, db):
            logger.warning(f"Course with ID {course_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Course with ID {course_id} not found"
            )

        # This query is complex and works well with raw SQL
        # We'll keep it as raw SQL for now but using SQLAlchemy text()
        from sqlalchemy import text
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
                ce.progress,
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
            ORDER BY
                ce.progress DESC
        """)
        
        result = await db.execute(query, {"course_id": course_id})
        
        return [
            StudentProgress(
                student_id=str(row[0]),
                progress=row[1] or str(0),  # Default to 0 if None
                last_activity=row[2],
                completed_assignments=row[3],
                total_assignments=row[4]
            ) for row in result.fetchall()
        ]
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving progress data for course {course_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to retrieve progress data: {str(e)}"
        )

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
        # Check permissions
        await check_user_permissions(current_user, ADMIN_ROLES)
        
        # Check if course exists using SQLAlchemy ORM
        if not await validate_course_exists(course_id, db):
            logger.warning(f"Course with ID {course_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Course with ID {course_id} not found"
            )
        
        # Get all enrollments for this course with user info using SQLAlchemy ORM
        stmt = (
            select(
                CourseEnrollment.id, 
                CourseEnrollment.student_id,
                User.name,
                User.email,
                User.picture,
                CourseEnrollment.status,
                CourseEnrollment.enrollment_date,
                CourseEnrollment.progress,
                CourseEnrollment.last_activity,
                CourseEnrollment.grade,
                CourseEnrollment.completion_date
            )
            .join(User, CourseEnrollment.student_id == User.id)
            .where(CourseEnrollment.course_id == course_id)
            .order_by(User.name)
        )
        
        result = await db.execute(stmt)
        
        return [
            {
                "id": str(row.id),
                "student_id": str(row.student_id),
                "name": row.name,
                "email": row.email,
                "picture": row.picture,
                "status": row.status,
                "enrollment_date": row.enrollment_date,
                "progress": row.progress,
                "last_activity": row.last_activity,
                "grade": row.grade,
                "completion_date": row.completion_date
            } for row in result
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving enrollments for course {course_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to retrieve enrollments"
        )

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
        # Get the student_id for this enrollment using SQLAlchemy ORM
        stmt = (
            select(CourseEnrollment.student_id)
            .where(
                and_(
                    CourseEnrollment.id == enrollment_id,
                    CourseEnrollment.course_id == course_id
                )
            )
        )
        
        result = await db.execute(stmt)
        enrollment_record = result.first()
        
        if not enrollment_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Enrollment with ID {enrollment_id} not found for course {course_id}"
            )
            
        student_id = str(enrollment_record[0])
        
        # Check permissions - allow staff or the student themselves
        await check_user_permissions(
            current_user, 
            ADMIN_ROLES, 
            student_id=student_id
        )
        
        # Check if course exists
        if not await validate_course_exists(course_id, db):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Course with ID {course_id} not found"
            )
        
        # Get enrollment details using SQLAlchemy ORM
        stmt = (
            select(
                CourseEnrollment.id, 
                CourseEnrollment.student_id,
                User.name,
                User.email,
                User.picture,
                CourseEnrollment.status,
                CourseEnrollment.enrollment_date,
                CourseEnrollment.progress,
                CourseEnrollment.last_activity,
                CourseEnrollment.grade,
                CourseEnrollment.completion_date
            )
            .join(User, CourseEnrollment.student_id == User.id)
            .where(
                and_(
                    CourseEnrollment.id == enrollment_id,
                    CourseEnrollment.course_id == course_id
                )
            )
        )
        
        result = await db.execute(stmt)
        enrollment_row = result.first()
        
        if not enrollment_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Could not retrieve details for enrollment ID {enrollment_id}"
            )
        
        enrollment = {
            "id": str(enrollment_row.id),
            "student_id": str(enrollment_row.student_id),
            "name": enrollment_row.name,
            "email": enrollment_row.email,
            "picture": enrollment_row.picture,
            "status": enrollment_row.status,
            "enrollment_date": enrollment_row.enrollment_date,
            "progress": enrollment_row.progress,
            "last_activity": enrollment_row.last_activity,
            "grade": enrollment_row.grade,
            "completion_date": enrollment_row.completion_date,
            "assignments": []
        }
        
        # Get assignment completion data using SQLAlchemy
        # This query is a bit complex but can be expressed with SQLAlchemy ORM
        from sqlalchemy import outerjoin
        from app.models.assignment import Assignment
        from app.models.submission import Submission
        
        stmt = (
            select(
                Assignment.id,
                Assignment.title,
                Submission.id.label("submission_id"),
                Submission.status.label("submission_status"),
                Submission.score,
                Submission.submitted_at
            )
            .select_from(Assignment)
            .outerjoin(
                Submission, 
                and_(
                    Assignment.id == Submission.assignment_id,
                    Submission.student_id == enrollment["student_id"]
                )
            )
            .where(Assignment.course_id == course_id)
            .order_by(Assignment.title)
        )
        
        result = await db.execute(stmt)
        
        enrollment["assignments"] = [
            {
                "id": str(row.id),
                "title": row.title,
                "submission_id": str(row.submission_id) if row.submission_id else None,
                "submission_status": row.submission_status,
                "score": row.score,
                "submitted_at": row.submitted_at
            } for row in result
        ]
            
        return enrollment
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving enrollment details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to retrieve enrollment details: {str(e)}"
        )

class EnrollmentRequest(BaseModel):
    course_id: UUID
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

        # Check user permissions using the permission model from main branch
        await check_user_permissions(current_user, ADMIN_ROLES)

        course_id = enrollment_data.course_id
        student_emails = enrollment_data.student_emails
        logger.info(f"Enrolling students: {student_emails} into course: {course_id}")

        # Check if course exists using SQLAlchemy ORM
        if not await validate_course_exists(course_id, db):
            logger.error(f"Course not found: {course_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Course with ID {course_id} not found"
            )

        logger.info(f"Course found: {course_id}. Fetching student details...")

        # Get students by email using SQLAlchemy ORM
        stmt = select(User).where(User.email.in_(student_emails))
        result = await db.execute(stmt)
        students = result.scalars().all()

        if not students:
            logger.warning("No valid students found for enrollment.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="No valid students found for enrollment"
            )

        logger.info(f"Found {len(students)} students. Checking for existing enrollments...")

        # Prepare enrollments
        enrollments = []
        for student in students:
            # Check if student is already enrolled
            stmt = select(CourseEnrollment).where(
                and_(
                    CourseEnrollment.student_id == student.id, 
                    CourseEnrollment.course_id == course_id
                )
            )
            result = await db.execute(stmt)
            existing_enrollment = result.scalar_one_or_none()
            
            if existing_enrollment is None:  # Avoid duplicates
                logger.info(f"Enrolling student {student.email} (ID: {student.id}) into course {course_id}")
                enrollment_obj = CourseEnrollment(
                    course_id=course_id,
                    student_id=student.id, 
                    user_id=current_user.get("id")
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to enroll students: {str(e)}"
        )

@router.delete("/{course_id}/students/{student_id}", response_model=Dict)
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
        # Check user permissions using the permission model from main branch
        await check_user_permissions(current_user, ADMIN_ROLES)

        # Check if course exists using SQLAlchemy ORM
        if not await validate_course_exists(course_id, db):
            logger.error(f"Course not found: {course_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Course with ID {course_id} not found"
            )

        # Check if student is enrolled using SQLAlchemy ORM
        stmt = select(CourseEnrollment).where(
            and_(
                CourseEnrollment.student_id == student_id, 
                CourseEnrollment.course_id == course_id
            )
        )
        result = await db.execute(stmt)
        enrollment = result.scalar_one_or_none()
        
        if not enrollment:
            logger.error(f"Student {student_id} is not enrolled in course {course_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Student is not enrolled in this course"
            )

        # Remove student from course
        logger.info(f"Removing student {student_id} from course {course_id}")
        await db.delete(enrollment)
        await db.commit()
        logger.info(f"Successfully removed student {student_id} from course {course_id}")
        
        # Verify removal
        stmt = select(CourseEnrollment).where(
            and_(
                CourseEnrollment.student_id == student_id, 
                CourseEnrollment.course_id == course_id
            )
        )
        result = await db.execute(stmt)
        remaining = result.scalar_one_or_none()
        logger.info(f"Remaining enrollment after delete: {remaining}")  # Should be None
        
        return {"message": "Student removed from course"}

    except HTTPException as e:
        await db.rollback()
        logger.error(f"Failed to remove student from course: {str(e)}")
        raise e

    except Exception as e:
        await db.rollback()
        logger.error(f"Error removing student from course: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to remove student from course: {str(e)}"
        ) 