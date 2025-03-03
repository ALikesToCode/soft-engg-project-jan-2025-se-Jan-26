from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import get_current_user
from app.routes.auth import require_role
from app.services.course_service import CourseService
from typing import List
from uuid import UUID

router = APIRouter(tags=["courses"])

@router.get("/user/courses/history",
    summary="Get user's course history",
    description="Retrieves the course history for the currently authenticated user",
    response_model=List[dict],
    responses={
        200: {
            "description": "Course history retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Data Structures and Algorithms",
                            "code": "CS201",
                            "semester": "Fall 2023",
                            "status": "completed",
                            "grade": "A",
                            "credits": 3
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Unauthorized - User not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        }
    }
)
async def get_course_history(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the course history for the current user.
    
    This endpoint returns a list of all courses the user has taken or is currently taking,
    including details like grades, completion status, etc.
    
    Returns:
        List of course objects with their details
    """
    try:
        courses = await CourseService.get_user_course_history(db, current_user["sub"])
        return courses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/faculty/courses/{course_id}/enrollment",
    summary="Get course enrollment",
    description="Retrieves the enrollment list for a specific course. Only accessible by faculty.",
    response_model=List[dict],
    responses={
        200: {
            "description": "Course enrollment retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "student_id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "John Doe",
                            "email": "john.doe@example.com",
                            "enrollment_date": "2023-08-15T00:00:00Z",
                            "status": "active"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Unauthorized - User not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        },
        403: {
            "description": "Forbidden - User is not a faculty member",
            "content": {
                "application/json": {
                    "example": {"detail": "Insufficient permissions"}
                }
            }
        }
    }
)
async def get_course_enrollment(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("faculty"))
):
    """
    Get the enrollment list for a specific course.
    
    This endpoint allows faculty members to view all students enrolled in a course.
    
    Args:
        course_id: UUID of the course
        
    Returns:
        List of enrolled students with their details
    """
    try:
        enrollment = await CourseService.get_course_enrollment(db, course_id)
        return enrollment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/support/courses/assignments",
    summary="Get all course assignments",
    description="Retrieves all assignments across all courses. Only accessible by support staff.",
    response_model=List[dict],
    responses={
        200: {
            "description": "Course assignments retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "course_id": "234f5678-f90a-23e4-b567-537725285111",
                            "course_name": "Data Structures and Algorithms",
                            "title": "Assignment 1",
                            "due_date": "2024-03-15T23:59:59Z",
                            "status": "active"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Unauthorized - User not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        },
        403: {
            "description": "Forbidden - User is not a support staff member",
            "content": {
                "application/json": {
                    "example": {"detail": "Insufficient permissions"}
                }
            }
        }
    }
)
async def get_all_course_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("support"))
):
    """
    Get all assignments across all courses.
    
    This endpoint allows support staff to view all assignments in the system.
    
    Returns:
        List of assignments with their details
    """
    try:
        assignments = await CourseService.get_all_course_assignments(db)
        return assignments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 