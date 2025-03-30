import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, and_, select
from enum import Enum
from pydantic import BaseModel

from app.database import get_db
from app.services.auth_service import get_current_user
from app.schemas.enrollment import StudentInfo, StudentProgress

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
    """Validate that a course exists in the database."""
    query = text("SELECT EXISTS(SELECT 1 FROM courses WHERE id = :course_id)")
    result = await db.execute(query, {"course_id": course_id})
    return result.scalar()

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
        # Check if course exists
        if not await validate_course_exists(course_id, db):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
            
        # Get all students for this course using raw SQL query with explicit JOIN
        # Ensure we're using student_id from course_enrollments to join with users.id
        query = text("""
            SELECT 
                u.id, 
                u.name, 
                u.email, 
                u.picture as avatar, 
                ce.enrollment_date, 
                ce.status
            FROM 
                course_enrollments ce
            JOIN 
                users u ON ce.student_id = u.id
            WHERE 
                ce.course_id = :course_id
            ORDER BY 
                u.name
        """)
        
        result = await db.execute(query, {"course_id": course_id})
        students = result.fetchall()
        
        # Map students to schema
        return [
            StudentInfo(
                id=str(student.id),
                name=student.name,
                email=student.email,
                avatar=student.avatar,
                enrollment_date=student.enrollment_date,
                status=student.status
            ) for student in students
        ]
            
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

        # Get all students' progress for this course using raw SQL
        # The join structure is defined in the CTE, with course_enrollments as the base table
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
                ce.last_activity,
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
                progress=row[1] or 0,  # Default to 0 if None
                last_activity=row[2],
                completed_assignments=row[3],
                total_assignments=row[4]
            ) for row in result.fetchall()
        ]
        
    except HTTPException:
        raise
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
        
        # Check if course exists
        if not await validate_course_exists(course_id, db):
            logger.warning(f"Course with ID {course_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Course with ID {course_id} not found"
            )
        
        # Get all enrollments for this course with user info using raw SQL
        query = text("""
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
                ce.completion_date
            FROM 
                course_enrollments ce
            JOIN 
                users u ON ce.student_id = u.id
            WHERE 
                ce.course_id = :course_id
            ORDER BY 
                u.name
        """)
        
        result = await db.execute(query, {"course_id": course_id})
        
        return [
            {
                "id": str(row[0]),
                "student_id": str(row[1]),
                "name": row[2],
                "email": row[3],
                "picture": row[4],
                "status": row[5],
                "enrollment_date": row[6],
                "progress": row[7],
                "last_activity": row[8],
                "grade": row[9],
                "completion_date": row[10]
            } for row in result.fetchall()
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
        # Get the student_id for this enrollment using raw SQL
        enrollment_query = text("""
            SELECT student_id FROM course_enrollments 
            WHERE id = :enrollment_id AND course_id = :course_id
        """)
        
        result = await db.execute(
            enrollment_query, 
            {"enrollment_id": enrollment_id, "course_id": course_id}
        )
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
        
        # Get enrollment details using raw SQL
        # Start with course_enrollments table and join users on student_id
        query = text("""
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
                ce.completion_date
            FROM 
                course_enrollments ce
            JOIN 
                users u ON ce.student_id = u.id
            WHERE 
                ce.id = :enrollment_id AND ce.course_id = :course_id
        """)
        
        result = await db.execute(query, {"enrollment_id": enrollment_id, "course_id": course_id})
        enrollment_row = result.first()
        
        if not enrollment_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Could not retrieve details for enrollment ID {enrollment_id}"
            )
        
        enrollment = {
            "id": str(enrollment_row[0]),
            "student_id": str(enrollment_row[1]),
            "name": enrollment_row[2],
            "email": enrollment_row[3],
            "picture": enrollment_row[4],
            "status": enrollment_row[5],
            "enrollment_date": enrollment_row[6],
            "progress": enrollment_row[7],
            "last_activity": enrollment_row[8],
            "grade": enrollment_row[9],
            "completion_date": enrollment_row[10],
            "assignments": []
        }
        
        # Get assignment completion data for this enrollment using raw SQL
        query = text("""
            SELECT 
                a.id,
                a.title,
                s.id as submission_id,
                s.status as submission_status,
                s.score,
                s.submitted_at
            FROM 
                assignments a
            LEFT JOIN 
                submissions s ON a.id = s.assignment_id AND s.student_id = :student_id
            WHERE 
                a.course_id = :course_id
            ORDER BY 
                a.title
        """)
        
        result = await db.execute(query, {"student_id": enrollment["student_id"], "course_id": course_id})
        
        enrollment["assignments"] = [
            {
                "id": str(row[0]),
                "title": row[1],
                "submission_id": str(row[2]) if row[2] else None,
                "submission_status": row[3],
                "score": row[4],
                "submitted_at": row[5]
            } for row in result.fetchall()
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