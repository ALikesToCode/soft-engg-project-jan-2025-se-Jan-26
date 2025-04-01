from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import get_current_user, require_auth
from app.routes.auth import require_role
from app.services.course_service import CourseService
from typing import List, Optional, Dict
from uuid import UUID
from app.services.function_router import function_router
from pydantic import BaseModel, UUID4
import logging

logger = logging.getLogger(__name__)

class CourseBookmarkData(BaseModel):
    course_id: UUID
    type: str
    title: str
    author: str

class EnrollmentCreate(BaseModel):
    student_id: UUID4
    status: Optional[str] = None

class EnrollmentStatusUpdate(BaseModel):
    status: str

class BulkEnrollment(BaseModel):
    student_ids: List[UUID4]

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
        return courses if courses else []
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        print("Error ==>", e)
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/user/recommended-courses",
    summary="Get User Recommended Courses",
    description="Retrieves recommended courses for the currently authenticated user",
    response_model=List[dict],
    responses={
        200: {
            "description": "Recommended courses retrieved successfully"
        },
        401: {
            "description": "Unauthorized - User not authenticated"
        },
        404: {
            "description": "User not found"
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def get_user_recommended_courses(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Get recommended courses for the current user.
    
    This endpoint returns a list of courses recommended for the user based on their
    preferences, past courses, and other factors.
    
    Returns:
        List of recommended course objects with their details
    """
    try:
        user_id = current_user['sub']
        courses = await CourseService.get_user_recommended_courses(db, user_id)
        return courses
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Error fetching recommended courses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve recommended courses: {str(e)}")
    
@router.get("/user/bookmarked-materials",
    summary="Get User Bookmarked Materials",
    description="Retrieves bookmarked materials for the currently authenticated user",
    response_model=List[dict],
    responses={
        200: {
            "description": "Bookmarked materials retrieved successfully"
        },
        401: {
            "description": "Unauthorized - User not authenticated"
        },
        404: {
            "description": "User not found"
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def get_user_bookmarked_materials(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Get bookmarked materials for the current user.
    
    This endpoint returns a list of all materials (lectures, resources, etc.) that
    the user has bookmarked across various courses.
    
    Returns:
        List of bookmarked material objects with their details
    """
    try:
        user_id = current_user['sub']
        bookmarked_materials = await CourseService.get_user_bookmarked_materials(db, user_id)
        return bookmarked_materials
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Error fetching bookmarked materials: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve bookmarked materials: {str(e)}")

@router.post("/user/bookmarked-materials",
    summary="Add User Bookmarked Materials",
    description="Adds a new bookmarked material for the currently authenticated user",
    response_model=dict,
    responses={
        200: {
            "description": "Material bookmarked successfully"
        },
        400: {
            "description": "Material already bookmarked"
        },
        401: {
            "description": "Unauthorized - User not authenticated"
        },
        404: {
            "description": "User or Course not found"
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def add_user_bookmarked_materials(
    bookmark_data: CourseBookmarkData,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Add a new bookmarked material for the current user.
    
    This endpoint allows users to bookmark course materials like lectures,
    resources, assignments, etc. for later access.
    
    Args:
        bookmark_data: Data for the new bookmark, including course ID, material type,
                      title, and author
    
    Returns:
        Details of the newly created bookmark
    """
    try:
        user_id = current_user['sub']
        bookmark = await CourseService.add_user_bookmarked_materials(bookmark_data, db, user_id)
        return bookmark
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Error adding bookmark: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add bookmark: {str(e)}")


@router.delete("/user/bookmarked-materials/{bookmark_id}",
    summary="Delete Bookmarked Material",
    description="Removes a bookmarked material for the currently authenticated user",
    response_model=List[dict],
    responses={
        200: {
            "description": "Bookmark deleted and updated list returned"
        },
        401: {
            "description": "Unauthorized - User not authenticated"
        },
        404: {
            "description": "User or Bookmark not found"
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def delete_bookmarked_material(
    bookmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Delete a bookmarked material for the current user.
    
    This endpoint removes a previously bookmarked material and returns
    the updated list of bookmarks.
    
    Args:
        bookmark_id: ID of the bookmark to delete
    
    Returns:
        Updated list of bookmarked materials
    """
    try:
        user_id = current_user['sub']
        updated_bookmarks = await CourseService.delete_bookmarked_material(db, user_id, bookmark_id)
        return updated_bookmarks
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Error deleting bookmark: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete bookmark: {str(e)}")

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

@router.post("/faculty/courses/{course_id}/enrollment",
    summary="Enroll a student in a course",
    description="Creates a new enrollment for a student in a specific course. Only accessible by faculty.",
    response_model=Dict,
    responses={
        200: {
            "description": "Student enrolled successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "course_id": "234f5678-f90a-23e4-b567-537725285111",
                        "student_id": "345g6789-g01b-34e5-c678-648836396222",
                        "status": "enrolled",
                        "enrollment_date": "2024-03-30T12:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Bad request - Invalid request or student already enrolled",
            "content": {
                "application/json": {
                    "example": {"detail": "Student is already enrolled in this course"}
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
async def enroll_student_by_faculty(
    course_id: UUID,
    enrollment: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("faculty"))
):
    """
    Enroll a student in a course (faculty access).
    
    This endpoint allows faculty members to enroll a student in their course.
    
    Args:
        course_id: UUID of the course
        enrollment: Request body containing student ID and optional status
        
    Returns:
        Enrollment details
    """
    try:
        # Optional: Check if faculty is teaching this course
        # This can be added for extra security
        
        result = await CourseService.enroll_student(
            db=db,
            course_id=course_id,
            student_id=enrollment.student_id,
            user_id=UUID(current_user["sub"]),
            status=enrollment.status if enrollment.status else None
        )
        return result
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/faculty/courses/enrollment/{enrollment_id}",
    summary="Update enrollment status",
    description="Updates the status of a student's enrollment in a course. Only accessible by faculty.",
    response_model=Dict,
    responses={
        200: {
            "description": "Enrollment status updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "course_id": "234f5678-f90a-23e4-b567-537725285111",
                        "student_id": "345g6789-g01b-34e5-c678-648836396222",
                        "status": "completed",
                        "enrollment_date": "2024-03-15T00:00:00Z",
                        "completion_date": "2024-03-30T12:00:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Not found - Enrollment does not exist",
            "content": {
                "application/json": {
                    "example": {"detail": "Enrollment not found"}
                }
            }
        }
    }
)
async def update_enrollment_status_by_faculty(
    enrollment_id: UUID,
    status_update: EnrollmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("faculty"))
):
    """
    Update enrollment status (faculty access).
    
    This endpoint allows faculty members to update a student's enrollment status
    (e.g., from enrolled to completed).
    
    Args:
        enrollment_id: UUID of the enrollment to update
        status_update: Request body containing the new status
        
    Returns:
        Updated enrollment details
    """
    try:
        result = await CourseService.update_enrollment_status(
            db=db,
            enrollment_id=enrollment_id,
            status=status_update.status
        )
        return result
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/faculty/courses/enrollment/{enrollment_id}",
    summary="Delete course enrollment",
    description="Removes a student from a course by deleting their enrollment. Only accessible by faculty.",
    response_model=Dict,
    responses={
        200: {
            "description": "Enrollment deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Enrollment deleted successfully",
                        "course_id": "234f5678-f90a-23e4-b567-537725285111",
                        "student_id": "345g6789-g01b-34e5-c678-648836396222"
                    }
                }
            }
        },
        404: {
            "description": "Not found - Enrollment does not exist",
            "content": {
                "application/json": {
                    "example": {"detail": "Enrollment not found"}
                }
            }
        }
    }
)
async def delete_enrollment_by_faculty(
    enrollment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("faculty"))
):
    """
    Delete course enrollment (faculty access).
    
    This endpoint allows faculty members to remove a student from a course.
    
    Args:
        enrollment_id: UUID of the enrollment to delete
        
    Returns:
        Confirmation message
    """
    try:
        result = await CourseService.delete_enrollment(
            db=db,
            enrollment_id=enrollment_id
        )
        return result
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/faculty/courses/{course_id}/bulk-enrollment",
    summary="Bulk enroll students",
    description="Enrolls multiple students in a course at once. Only accessible by faculty.",
    response_model=Dict,
    responses={
        200: {
            "description": "Bulk enrollment completed",
            "content": {
                "application/json": {
                    "example": {
                        "course_id": "234f5678-f90a-23e4-b567-537725285111",
                        "successful": [
                            {
                                "student_id": "345g6789-g01b-34e5-c678-648836396222",
                                "status": "enrolled"
                            }
                        ],
                        "failed": [
                            {
                                "student_id": "456h7890-h12c-45f6-d789-759947407333",
                                "reason": "Already enrolled"
                            }
                        ],
                        "total_enrolled": 1,
                        "total_waitlisted": 0,
                        "total_failed": 1
                    }
                }
            }
        }
    }
)
async def bulk_enroll_students_by_faculty(
    course_id: UUID,
    enrollment: BulkEnrollment,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("faculty"))
):
    """
    Bulk enroll students (faculty access).
    
    This endpoint allows faculty members to enroll multiple students in their course at once.
    
    Args:
        course_id: UUID of the course
        enrollment: Request body containing list of student IDs
        
    Returns:
        Summary of enrollment results
    """
    try:
        result = await CourseService.bulk_enroll_students(
            db=db,
            course_id=course_id,
            student_ids=enrollment.student_ids,
            user_id=UUID(current_user["sub"])
        )
        return result
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Support staff endpoints - similar to faculty endpoints but with support role requirement

@router.post("/support/courses/{course_id}/enrollment",
    summary="Enroll a student in a course (Support)",
    description="Creates a new enrollment for a student in a specific course. Only accessible by support staff.",
    response_model=Dict,
    responses={
        200: {
            "description": "Student enrolled successfully"
        },
        400: {
            "description": "Bad request - Invalid request or student already enrolled"
        },
        403: {
            "description": "Forbidden - User is not a support staff member"
        }
    }
)
async def enroll_student_by_support(
    course_id: UUID,
    enrollment: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("support"))
):
    """
    Enroll a student in a course (support access).
    
    This endpoint allows support staff to enroll a student in any course.
    
    Args:
        course_id: UUID of the course
        enrollment: Request body containing student ID and optional status
        
    Returns:
        Enrollment details
    """
    try:
        result = await CourseService.enroll_student(
            db=db,
            course_id=course_id,
            student_id=enrollment.student_id,
            user_id=UUID(current_user["sub"]),
            status=enrollment.status if enrollment.status else None
        )
        return result
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/support/courses/enrollment/{enrollment_id}",
    summary="Update enrollment status (Support)",
    description="Updates the status of a student's enrollment in a course. Only accessible by support staff.",
    response_model=Dict,
    responses={
        200: {
            "description": "Enrollment status updated successfully"
        },
        404: {
            "description": "Not found - Enrollment does not exist"
        }
    }
)
async def update_enrollment_status_by_support(
    enrollment_id: UUID,
    status_update: EnrollmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("support"))
):
    """
    Update enrollment status (support access).
    
    This endpoint allows support staff to update any student's enrollment status.
    
    Args:
        enrollment_id: UUID of the enrollment to update
        status_update: Request body containing the new status
        
    Returns:
        Updated enrollment details
    """
    try:
        result = await CourseService.update_enrollment_status(
            db=db,
            enrollment_id=enrollment_id,
            status=status_update.status
        )
        return result
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/support/courses/enrollment/{enrollment_id}",
    summary="Delete course enrollment (Support)",
    description="Removes a student from a course by deleting their enrollment. Only accessible by support staff.",
    response_model=Dict,
    responses={
        200: {
            "description": "Enrollment deleted successfully"
        },
        404: {
            "description": "Not found - Enrollment does not exist"
        }
    }
)
async def delete_enrollment_by_support(
    enrollment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("support"))
):
    """
    Delete course enrollment (support access).
    
    This endpoint allows support staff to remove any student from any course.
    
    Args:
        enrollment_id: UUID of the enrollment to delete
        
    Returns:
        Confirmation message
    """
    try:
        result = await CourseService.delete_enrollment(
            db=db,
            enrollment_id=enrollment_id
        )
        return result
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/support/courses/{course_id}/bulk-enrollment",
    summary="Bulk enroll students (Support)",
    description="Enrolls multiple students in a course at once. Only accessible by support staff.",
    response_model=Dict,
    responses={
        200: {
            "description": "Bulk enrollment completed"
        }
    }
)
async def bulk_enroll_students_by_support(
    course_id: UUID,
    enrollment: BulkEnrollment,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("support"))
):
    """
    Bulk enroll students (support access).
    
    This endpoint allows support staff to enroll multiple students in any course at once.
    
    Args:
        course_id: UUID of the course
        enrollment: Request body containing list of student IDs
        
    Returns:
        Summary of enrollment results
    """
    try:
        result = await CourseService.bulk_enroll_students(
            db=db,
            course_id=course_id,
            student_ids=enrollment.student_ids,
            user_id=UUID(current_user["sub"])
        )
        return result
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 