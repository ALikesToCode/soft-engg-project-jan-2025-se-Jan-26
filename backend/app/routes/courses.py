from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import get_current_user, require_auth
from app.routes.auth import require_role
from app.services.course_service import CourseService
from typing import List, Optional
from uuid import UUID
from app.services.function_router import function_router
from pydantic import BaseModel

class CourseBookmarkData(BaseModel):
    course_id: UUID
    type: str
    title: str
    author: str

router = APIRouter(tags=["User Courses"])
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
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        print("Error ==>", e)
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/user/recommended-courses")
async def get_user_recommended_courses(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    user_id = current_user['sub']
    try:
        courses = await CourseService.get_user_recommended_courses(db, user_id)
        return courses
    except Exception as e:
        raise HTTPException(status=500, detail=str(e))
    
@router.get("/user/bookmarked-materials")
async def get_user_bookmarked_materials(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    user_id = current_user['sub']
    try:
        bookmarkeds = await CourseService.get_user_bookmarked_materials(db, user_id)
        return bookmarkeds
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status=500, detail=str(e))

@router.post("/user/bookmarked-materials")
async def add_user_bookmarked_materials(
    bookmark_data: CourseBookmarkData,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    user_id = current_user['sub']
    try:
        bookmarkeds = await CourseService.add_user_bookmarked_materials(bookmark_data,db, user_id)
        return bookmarkeds
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status=500, detail=str(e))


@router.delete("/user/bookmarked-materials/{bookmark_id}")
async def delete_bookmarked_material(
    bookmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    user_id = current_user['sub']
    try:
        bookmarkeds = await CourseService.delete_bookmarked_material(db, user_id, bookmark_id)
        return bookmarkeds
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status=500, detail=str(e))

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
    except HTTPException as http_ex:
        raise http_ex
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

@function_router.function_declaration(
    name="get_courses",
    description="Get a list of available courses, optionally filtered by category",
    parameters={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Course category (e.g., 'programming', 'data-science', 'all')",
                "default": "all"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of courses to return",
                "default": 10
            }
        }
    }
)
async def get_courses(category: str = "all", limit: int = 10):
    """Get available courses with optional category filter"""
    # This is a mock implementation - replace with actual database query
    courses = {
        "programming": [
            {"id": "cs101", "title": "Introduction to Programming", "description": "Learn programming basics"},
            {"id": "cs201", "title": "Data Structures", "description": "Advanced programming concepts"},
        ],
        "data-science": [
            {"id": "ds101", "title": "Data Science Fundamentals", "description": "Introduction to data science"},
            {"id": "ml101", "title": "Machine Learning", "description": "Basic machine learning concepts"},
        ]
    }
    
    if category == "all":
        all_courses = []
        for cat_courses in courses.values():
            all_courses.extend(cat_courses)
        return all_courses[:limit]
    
    if category not in courses:
        raise HTTPException(status_code=404, detail=f"Category {category} not found")
    
    return courses[category][:limit]

@function_router.function_declaration(
    name="search_courses",
    description="Search for courses by keyword",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query string"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results",
                "default": 5
            }
        },
        "required": ["query"]
    }
)
async def search_courses(query: str, limit: int = 5):
    """Search for courses by keyword"""
    # Mock implementation - replace with actual search logic
    all_courses = await get_courses(category="all")
    
    # Simple search implementation
    query = query.lower()
    matches = [
        course for course in all_courses
        if query in course["title"].lower() or query in course["description"].lower()
    ]
    
    return matches[:limit]

@function_router.function_declaration(
    name="get_course_details",
    description="Get detailed information about a specific course",
    parameters={
        "type": "object",
        "properties": {
            "course_id": {
                "type": "string",
                "description": "The ID of the course"
            }
        },
        "required": ["course_id"]
    }
)
async def get_course_details(course_id: str):
    """Get detailed information about a specific course"""
    # Mock implementation - replace with actual database query
    all_courses = await get_courses(category="all")
    
    for course in all_courses:
        if course["id"] == course_id:
            # Add more details for the course
            return {
                **course,
                "duration": "12 weeks",
                "prerequisites": ["None"],
                "syllabus": [
                    "Week 1: Introduction",
                    "Week 2: Basic Concepts",
                    "Week 3-11: Main Content",
                    "Week 12: Final Project"
                ],
                "instructors": ["Dr. Smith"],
                "rating": 4.5,
                "enrolled_students": 150
            }
    
    raise HTTPException(status_code=404, detail=f"Course {course_id} not found") 