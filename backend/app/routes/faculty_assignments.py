import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from pydantic import BaseModel

from app.database import get_db
from app.services.auth_service import get_current_user, require_role
from app.models.course import Course
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["faculty_assignments"])

class FacultyAssignmentCreate(BaseModel):
    courseId: UUID
    facultyId: UUID
    capacity: int

class CapacityUpdate(BaseModel):
    capacity: int

# Get all faculty assignments
@router.get("/courses/assignments", response_model=List[Dict])
async def get_faculty_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(require_role(["support", "admin", "superuser"]))
):
    """
    Get all faculty-course assignments.
    Only accessible by support, admin or superuser roles.
    """
    try:
        # Get all faculty assignments using SQLAlchemy ORM
        stmt = (
            select(
                Course.id, 
                Course.name.label("courseName"),
                Course.code.label("courseCode"),
                Course.faculty_id,
                User.name.label("facultyName"),
                User.email.label("facultyEmail"),
                Course.capacity,
                Course.enrolled_count.label("enrolledStudents"),
                Course.status
            )
            .join(User, Course.faculty_id == User.id)
            .order_by(Course.name)
        )
        
        result = await db.execute(stmt)
        
        return [
            {
                "id": str(row.id),
                "courseId": str(row.id),
                "courseName": row.courseName,
                "courseCode": row.courseCode,
                "facultyId": str(row.faculty_id),
                "facultyName": row.facultyName,
                "facultyEmail": row.facultyEmail,
                "capacity": row.capacity,
                "enrolledStudents": row.enrolledStudents,
                "status": row.status
            } for row in result
        ]
        
    except Exception as e:
        logger.error(f"Error retrieving faculty assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to retrieve faculty assignments: {str(e)}"
        )

# Assign faculty to a course
@router.post("/courses/assignments", response_model=Dict)
async def assign_faculty(
    assignment: FacultyAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(require_role(["support", "admin", "superuser"]))
):
    """
    Assign a faculty member to a course.
    Only accessible by support, admin or superuser roles.
    """
    try:
        # Check if course exists
        course_stmt = select(Course).where(Course.id == assignment.courseId)
        course_result = await db.execute(course_stmt)
        course = course_result.scalar_one_or_none()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with ID {assignment.courseId} not found"
            )
            
        # Check if faculty exists
        faculty_stmt = select(User).where(
            and_(
                User.id == assignment.facultyId,
                User.role == "faculty"
            )
        )
        faculty_result = await db.execute(faculty_stmt)
        faculty = faculty_result.scalar_one_or_none()
        
        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faculty with ID {assignment.facultyId} not found"
            )
            
        # Update course with faculty and capacity
        course.faculty_id = assignment.facultyId
        course.capacity = assignment.capacity
        
        await db.commit()
        await db.refresh(course)
        
        return {
            "id": str(course.id),
            "courseId": str(course.id),
            "facultyId": str(course.faculty_id),
            "capacity": course.capacity,
            "message": "Faculty assigned to course successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error assigning faculty to course: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign faculty to course: {str(e)}"
        )

# Remove faculty from a course
@router.delete("/courses/assignments/{assignment_id}", response_model=Dict)
async def remove_faculty_assignment(
    assignment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(require_role(["support", "admin", "superuser"]))
):
    """
    Remove faculty assignment from a course.
    Only accessible by support, admin or superuser roles.
    """
    try:
        # Get the course by ID
        stmt = select(Course).where(Course.id == assignment_id)
        result = await db.execute(stmt)
        course = result.scalar_one_or_none()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with ID {assignment_id} not found"
            )
            
        # Remove faculty assignment
        course.faculty_id = None
        
        await db.commit()
        
        return {
            "message": "Faculty assignment removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error removing faculty assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove faculty assignment: {str(e)}"
        )

# Bulk assign faculty to courses
@router.post("/courses/assignments/bulk", response_model=Dict)
async def bulk_assign_faculty(
    assignments: List[FacultyAssignmentCreate],
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(require_role(["support", "admin", "superuser"]))
):
    """
    Bulk assign faculty to multiple courses.
    Only accessible by support, admin or superuser roles.
    """
    try:
        successful_assignments = []
        failed_assignments = []
        
        for assignment in assignments:
            try:
                # Check if course exists
                course_stmt = select(Course).where(Course.id == assignment.courseId)
                course_result = await db.execute(course_stmt)
                course = course_result.scalar_one_or_none()
                
                if not course:
                    failed_assignments.append({
                        "courseId": str(assignment.courseId),
                        "reason": "Course not found"
                    })
                    continue
                    
                # Check if faculty exists
                faculty_stmt = select(User).where(
                    and_(
                        User.id == assignment.facultyId,
                        User.role == "faculty"
                    )
                )
                faculty_result = await db.execute(faculty_stmt)
                faculty = faculty_result.scalar_one_or_none()
                
                if not faculty:
                    failed_assignments.append({
                        "courseId": str(assignment.courseId),
                        "reason": "Faculty not found"
                    })
                    continue
                    
                # Update course with faculty and capacity
                course.faculty_id = assignment.facultyId
                course.capacity = assignment.capacity
                
                successful_assignments.append({
                    "courseId": str(assignment.courseId),
                    "facultyId": str(assignment.facultyId)
                })
                
            except Exception as e:
                failed_assignments.append({
                    "courseId": str(assignment.courseId),
                    "reason": str(e)
                })
                
        await db.commit()
        
        return {
            "message": f"Bulk assignment completed. Successfully assigned: {len(successful_assignments)}, Failed: {len(failed_assignments)}",
            "successful": successful_assignments,
            "failed": failed_assignments
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in bulk faculty assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process bulk assignments: {str(e)}"
        )

# Get available faculty
@router.get("/faculty/available", response_model=List[Dict])
async def get_available_faculty(
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(require_role(["support", "admin", "superuser"]))
):
    """
    Get all available faculty members.
    Only accessible by support, admin or superuser roles.
    """
    try:
        # Get all faculty members
        stmt = (
            select(User.id, User.name, User.email)
            .where(User.role == "faculty")
            .order_by(User.name)
        )
        
        result = await db.execute(stmt)
        
        return [
            {
                "id": str(row.id),
                "name": row.name,
                "email": row.email
            } for row in result
        ]
        
    except Exception as e:
        logger.error(f"Error retrieving available faculty: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve available faculty: {str(e)}"
        )

# Update course capacity
@router.put("/courses/{course_id}/capacity", response_model=Dict)
async def update_course_capacity(
    course_id: UUID,
    capacity_data: CapacityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(require_role(["support", "admin", "superuser", "faculty"]))
):
    """
    Update the capacity of a course.
    Accessible by support, admin, superuser, or the faculty assigned to the course.
    """
    try:
        # Get the course
        stmt = select(Course).where(Course.id == course_id)
        result = await db.execute(stmt)
        course = result.scalar_one_or_none()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with ID {course_id} not found"
            )
            
        # If user is faculty, check if they are assigned to this course
        if current_user.get("role") == "faculty" and str(course.faculty_id) != current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this course"
            )
            
        # Update course capacity
        course.capacity = capacity_data.capacity
        
        await db.commit()
        await db.refresh(course)
        
        return {
            "id": str(course.id),
            "capacity": course.capacity,
            "message": "Course capacity updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating course capacity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update course capacity: {str(e)}"
        )

# Get course enrollment statistics
@router.get("/courses/{course_id}/enrollment-stats", response_model=Dict)
async def get_course_enrollment_stats(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get enrollment statistics for a specific course.
    Accessible by faculty assigned to the course, support, admin, or superuser.
    """
    try:
        # Get the course
        stmt = select(Course).where(Course.id == course_id)
        result = await db.execute(stmt)
        course = result.scalar_one_or_none()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with ID {course_id} not found"
            )
            
        # Check permissions
        user_role = current_user.get("role")
        user_id = current_user.get("id")
        
        if user_role not in ["support", "admin", "superuser"] and str(course.faculty_id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this course's statistics"
            )
            
        # Get enrollment statistics
        from sqlalchemy import func
        from app.models.course import CourseEnrollment
        
        # Get count of students by status
        enrollment_stats_stmt = (
            select(
                CourseEnrollment.status,
                func.count(CourseEnrollment.id).label("count")
            )
            .where(CourseEnrollment.course_id == course_id)
            .group_by(CourseEnrollment.status)
        )
        
        enrollment_stats_result = await db.execute(enrollment_stats_stmt)
        enrollment_stats = {row.status: row.count for row in enrollment_stats_result}
        
        # Calculate completion rate
        total_enrollments = sum(enrollment_stats.values())
        completed = enrollment_stats.get("completed", 0)
        completion_rate = (completed / total_enrollments * 100) if total_enrollments > 0 else 0
        
        return {
            "course_id": str(course_id),
            "total_enrollments": total_enrollments,
            "capacity": course.capacity,
            "utilization_rate": (total_enrollments / course.capacity * 100) if course.capacity > 0 else 0,
            "enrollment_by_status": enrollment_stats,
            "completion_rate": completion_rate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving course enrollment statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve course enrollment statistics: {str(e)}"
        ) 