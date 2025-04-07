from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import require_auth
from app.services.course_service import *
from app.utils.helpers import LectureContentData, ModuleCreate, \
    UpdateLectureContentData, DocumentLinkCreate, UpdateDocumentLinkCreate
from app.models.course import Course, CourseStatus
from uuid import UUID
import uuid
from pydantic import BaseModel
from datetime import date
import logging

logger = logging.getLogger(__name__)

class CourseCreate(BaseModel):
    name: str
    code: str
    title: str
    credits: int
    duration: int
    semester: str
    year: int
    syllabus: str | None = None
    description: str | None = None
    start_date: date
    end_date: date
    level: str
class CourseCodeResponse(BaseModel):
    course_code: str

course_router = APIRouter(tags=["Faculty Courses"])

@course_router.get("/course-code", response_model=CourseCodeResponse)
async def get_unique_course_code(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)):
    try:
        code = await get_new_course_code(db, current_user["sub"])
        return CourseCodeResponse(course_code=code)
    except Exception as e:
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@course_router.get("/faculty/courses", response_model=list[dict],
    summary="Get faculty's courses",
    description="Retrieves all courses taught by the faculty",
    response_description="List of courses",
    responses={
        200: {
        "description": "Courses retrieved successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Introduction to Computer Science",
                    "code": "CS101",
                    "title": "Fundamentals of Computer Science",
                    "syllabus": "Introduction to Programming ,Data Structures, and Algorithms",
                    "description": "An introductory course covering fundamental concepts in computer science and programming.",
                    "credits": 3,
                    "duration": "16 weeks",
                    "semester": "Fall",
                    "year": 2025,
                    "status": "active",
                    "created_at": "2025-01-15T10:30:00Z",
                    "updated_at": "2025-02-20T14:45:00Z"
                    }
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
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }
)
async def fetch_courses(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_auth)): 
     
    # if current_user["role"] not in ["faculty", "admin", "support"]:
    #     raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        #Implemente code to check if user is faculty
        courses = await get_all_courses(db, current_user["sub"]) 
        return courses
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e: 
        logger.error(f"Error ==> {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


#GET MODULES FOR THE COURSE
@course_router.get("/courses/module/{course_id}", 
    summary="Get all modules for the course",
    description="Retrieves all modules for the given course",
    response_description="List of modules",
    responses={
        200: {
        "description": "Modules retrieved successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "course_id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Week 1",
                    "position": 1
                    }
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
            "description": "Forbidden - User does not have access to the course",
            "content": {
                "application/json": {
                    "example": {"detail": "Forbidden"}
                }
            }
        },
        404: {
            "description": "Module not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Module not found"}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }
)
async def get_modules_for_course(course_id: str,
            db: AsyncSession = Depends(get_db),
            current_user: dict = Depends(require_auth)): 
    try:
        modules = await get_modules_by_course(course_id,db, current_user['sub'])  
        return modules
    except Exception as e:
        logger.error("Error wile getting module ", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@course_router.get("/courses/module/lecture/{module_id}",
    summary="Get all lectures for the given module",
    description="Retrieves all lectures for the given module",
    response_description="List of lectures",
    responses={
        200: {
        "description": "Lectures retrieved successfully",
        "content": {
            "application/json": {
                "example": [{
                    "id": 1,
                    "module_id": 1,
                    "content_type": "lecture",
                    "title": "Introduction to Computer Science",
                    "description": "An introductory lecture on computer science",
                    "video_url": "https://www.youtube.com/watch?v=KM9nIFBoiUA"
                    }]
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
        404: {
            "description": "Module not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Module not found"}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }
)
async def get_lecture_for_given_module(module_id: str, 
                                       db: AsyncSession = Depends(get_db), 
                                       current_user: dict = Depends(require_auth)):
    try:
        module_id = int(module_id)
        modules = await get_lecture_for_module(module_id,db, current_user['sub'])  
        return modules
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@course_router.get("/courses/module/content/{module_id}",response_model=list[dict],
    summary="Get all lecture content for the given module",
    description="Retrieves all lecture content for the given module",
    response_description="List of lecture content",
    responses={
        200: {
        "description": "Lecture content retrieved successfully",
        "content": {
            "application/json": {
                "example": [
                    {
                    "id": 1,
                    "lecture_id": 1,
                    "title": "Introduction to Computer Science",
                    "content_url": "https://www.youtube.com/watch?v=KM9nIFBoiUA",
                    "content_desc": "An introductory lecture on computer science"
                    },
                    {
                    "id": 2,
                    "lecture_id": 1,
                    "title": "Introduction to Python",
                    "content_url": "https://www.youtube.com/watch?v=KM9nIFBoiUA",
                    "content_desc": "An introductory lecture on Python programming"
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
        404: {
            "description": "No Lecture found for the module",
            "content": {
                "application/json": {
                    "example": {"detail": "No Lecture found for the module"}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }

)
async def get_lecture_content(module_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_auth)):
    # lecture_id = int(lecture_id)
    module_id  = int(module_id)
    try:
        contents = await get_lecture_content_by_module(module_id,db, current_user['sub'])
        return contents
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.get("/courses/lecture/content/{lecture_id}", response_model=dict,
    summary="Get lecture content for the given lecture",
    description="Retrieves lecture content for the given lecture",
    response_description="Lecture content",
    responses={
        200: {
        "description": "Lecture content retrieved successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "lecture_id": 1,
                    "title": "Introduction to Computer Science",
                    "content_url": "https://www.youtube.com/watch?v=KM9nIFBoiUA",
                    "content_desc": "An introductory lecture on computer science"
                    }
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
        404: {
            "description": "No content found for the given lecture",
            "content": {
                "application/json": {
                    "example": {"detail": "No content found for the given lecture"}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }                   
)
async def get_video_lecture_content(lecture_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_auth)):
    try:
        lecture_id = int(lecture_id)
        content = await get_lecture_content_by_lecture(lecture_id, db, current_user['sub'])
        return content
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        print("Error => " + str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
@course_router.post("/courses/module/content/lecture", response_model=dict,
    summary="Add video lecture content to the module",
    description="Adds a new video lecture content to the module",
    response_description="Lecture content",
    responses={
        200: {
        "description": "Lecture content added successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "lecture_id": 1,
                    "title": "Introduction to Computer Science",
                    "content_url": "https://www.youtube.com/watch?v=KM9nIFBoiUA",
                    "content_desc": "An introductory lecture on computer science"
                    }
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
        404: {
            "description": "Module not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Module not found"}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }
)
async def add_content(content: LectureContentData, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_auth)):
    """
    Adds a new doc content to the lecture
    """
    try:
        doc_content_added = await add_lecture_content_to_existing_course(content, db, current_user['sub'])
        return doc_content_added
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.post("/courses/module",
    summary="Add a new module to the course",
    description="Adds a new module to the course",
    response_description="New module added",
    responses={
        200: {
        "description": "Module added successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "course_id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Week 1",
                    "position": 1
                    }
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
            "description": "Forbidden - You are not authorized to add modules to this course",
            "content": {
                "application/json": {
                    "example": {"detail": "Forbidden"}
                }
            }
        },
        404: {
            "description": "Course not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Course not found"}
                }
            }
        }, 
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }
)
async def create_module(module_data: ModuleCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_auth)):
    """
    Adds a new module to the course
    """
    try:
        new_module = await add_module(module_data, db, current_user['sub'])
        return new_module
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.post("/courses/module/doc_content/lecture", response_model=dict,
    summary="Add document content to the lecture",
    description="Adds a new document content to the lecture",
    response_description="Document content",
    responses={
        200: {
        "description": "Document content added successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "lecture_id": 1,
                    "lecture_title": "Introduction to Computer Science",
                    "file_type": "document",
                    "driveLink": "https://drive.google.com/file/d/",
                    "content_desc": "An introductory document on computer science"
                    }
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
        404: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "examples": {
                    "ModuleNotFound": {"value": {"detail": "Module not found"}},
                    "CourseNotFound": {"value": {"detail": "Course not found"}}
                    }
                }
            }
        },
        403: {
            "description": "Forbidden - You are not authorized to add content to this course",
            "content": {
                "application/json": {
                    "example": {"detail": "Forbidden"}
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
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }                    
)
async def add_doc_content(content: DocumentLinkCreate, db: AsyncSession = Depends(get_db),current_user: dict = Depends(require_auth)):
    """
    Adds a new doc content to the lecture
    """
    try:
        doc_content_added = await add_doc_content_to_existing_course(content, db, current_user['sub'])
        return doc_content_added
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.put("/courses/module/content/lecture", response_model=dict,
    summary="Update lecture content",
    description="Updates an existing lecture content in the module of a course",
    response_description="Updated lecture content",
    responses={
        200: {
        "description": "Lecture content updated successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "lecture_id": 1,
                    "title": "Introduction to Computer Science",
                    "content_url": "https://www.youtube.com/watch?v=KM9nIFBoiUA",
                    "content_desc": "An introductory lecture on computer science"
                    }
                }
            }
        },
        400: {
            "description": "Content type cannot be changed",
            "content": {
                "application/json": {
                "example": {"detail": "Content type cannot be changed"}
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
        404: {
            "description": "Not Found Errors",
            "content": {
                "application/json": {
                    "ModuleNotFound": {"value": {"detail": "Module not found"}},
                    "CourseNotFound": {"value": {"detail": "Course not found"}},
                    "LectureContentNotFound":{"value": {"detail": "LectureContent not found"}}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }
)
async def update_content(content: UpdateLectureContentData, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_auth)):
    """
    Updates an existing lecture content in the module of a course
    """
    try:
        updated_content = await update_existing_lecture_content(content, db, current_user['sub'])
        return updated_content
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.put("/courses/module/doc_content/lecture", response_model=dict,
    summary="Update document content",
    description="Updates an existing document content in the module of a course",
    response_description="Updated document content",
    responses={
        200: {
        "description": "Document content updated successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "lecture_id": 1,
                    "lecture_title": "Introduction to Computer Science",
                    "file_type": "document",
                    "driveLink": "https://drive.google.com/file/d/",
                    "content_desc": "An introductory document on computer science"
                    }
                }
            }
        },
        400: {
            "description": "Content type cannot be changed",
            "content": {
                "application/json": {
                "example": {"detail": "Content type cannot be changed"}
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
            "description": "Forbidden - You are not authorized to add content to this course",
            "content": {
                "application/json": {
                    "example": {"detail": "Forbidden"}
                }
            }
        },
        404: {
            "description": "Not Found Errors",
            "content": {
                "application/json": {
                    "ModuleNotFound": {"value": {"detail": "Module not found"}},
                    "CourseNotFound": {"value": {"detail": "Course not found"}},
                    "LectureContentNotFound":{"value": {"detail": "LectureContent not found"}}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }
)
async def update_doc_content(content: UpdateDocumentLinkCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_auth)):
    """
    Updates an existing doc content in the module of a course
    """
    try:
        updated_content = await update_existing_lecture_doc_content(content, db, current_user['sub'])
        return updated_content
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@course_router.delete("/courses/module/{module_id}",
    summary="Delete a module from the course",
    description="Deletes a module from the course",
    response_description="Module deleted",
    responses={
        200: {
            "description": "Module deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Module deleted successfully"}
                }
            }
        },
        404: {
            "description": "Module not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Module not found"}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }                      
)
async def delete_module(module_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_auth)):
    """
    Deletes a module from the course
    """
    try:
        module_id = int(module_id)
        deleted = await delete_module_by_id(module_id, db, current_user['sub'])
        if deleted:
            return {"message": "Module deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Module not found")
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.post("/courses", response_model=dict)
async def create_course(course_data: CourseCreate, 
                        db: AsyncSession = Depends(get_db),
                        current_user: dict = Depends(require_auth)):
    """
    Create a new course
    """
    user_id = current_user["sub"]
    try:
        new_course = await add_new_course(course_data, db, user_id)
        return new_course.to_dict()
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@course_router.get("/courses/{course_id}/students")
async def get_students_in_course(course_id: str, 
                            db: AsyncSession = Depends(get_db)):
    """
    Get all students in a course
    """
    try:
        students = await get_students_by_course(course_id, db)
        return students
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))