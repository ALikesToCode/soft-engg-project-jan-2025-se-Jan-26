import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import get_current_user
from app.schemas.enrollment import StudentInfo, StudentProgress

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/courses", tags=["enrollments"])

@router.get("/{course_id}/students", response_model=List[StudentInfo])
async def get_course_students(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all students enrolled in a specific course.
    Returns basic information about each student (id, name, email, avatar).
    """
    try:
        # Check user permissions (must be faculty or admin)
        if current_user.get("role") not in ["faculty", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to view this information")
        
        # Check if course exists
        query = """
            SELECT EXISTS(SELECT 1 FROM courses WHERE id = :course_id)
        """
        exists = await db.execute(query, {"course_id": str(course_id)})
        if not (await exists.fetchone())[0]:
            raise HTTPException(status_code=404, detail=f"Course with ID {course_id} not found")

        # Get all enrolled students for this course
        query = """
            SELECT 
                u.id, 
                u.name, 
                u.email, 
                u.picture as avatar,
                ce.enrollment_date,
                ce.status
            FROM 
                users u
            JOIN 
                course_enrollments ce ON u.id = ce.student_id
            WHERE 
                ce.course_id = :course_id
            ORDER BY 
                u.name
        """
        result = await db.execute(query, {"course_id": str(course_id)})
        students = []
        
        for row in await result.fetchall():
            student = {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "avatar": row[3],
                "enrollment_date": row[4],
                "status": row[5]
            }
            students.append(student)
            
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
        if current_user.get("role") not in ["faculty", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to view this information")
        
        # Check if course exists
        query = """
            SELECT EXISTS(SELECT 1 FROM courses WHERE id = :course_id)
        """
        exists = await db.execute(query, {"course_id": str(course_id)})
        if not (await exists.fetchone())[0]:
            raise HTTPException(status_code=404, detail=f"Course with ID {course_id} not found")

        # Get all students' progress for this course
        query = """
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
        """
        result = await db.execute(query, {"course_id": str(course_id)})
        progress_data = []
        
        for row in await result.fetchall():
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
        
    except Exception as e:
        logger.error(f"Error retrieving enrollment details for {enrollment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve enrollment details: {str(e)}") 