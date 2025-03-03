from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.course_service import CourseService
from app.utils.auth import require_role
from app.database.database import get_db

router = APIRouter()

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
        print(f"Error in get_all_course_assignments endpoint: {str(e)}")  # Log the error
        raise HTTPException(status_code=500, detail=str(e)) 