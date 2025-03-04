from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.course_service import *
from app.utils.helpers import LectureContentData, ModuleCreate, UpdateLectureContentData
from app.models.course import Course, CourseStatus
from uuid import UUID
from pydantic import BaseModel

class CourseCreate(BaseModel):
    name: str
    code: str
    title: str
    credits: int
    duration: int
    semester: str
    year: int
    faculty_id: UUID
    created_by: UUID
    syllabus: str | None = None
    description: str | None = None

course_router = APIRouter()

@course_router.get("/courses", response_model=list[dict])
async def fetch_courses(db: AsyncSession = Depends(get_db)):  
    try:
        courses = await get_all_courses(db)  
        return courses
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))


@course_router.get("/courses/module/{course_id}")
async def get_modules_for_course(course_id: str, db: AsyncSession = Depends(get_db)):
    try:
        course_id = int(course_id)
        modules = await get_modules_by_course(course_id,db)  
        return modules
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.get("/courses/module/lecture/{module_id}")
async def get_lecture_for_given_module(module_id: str, db: AsyncSession = Depends(get_db)):
    try:
        module_id = int(module_id)
        modules = await get_lecture_for_module(module_id,db)  
        return modules
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@course_router.get("/courses/module/content/{module_id}",response_model=list[dict])
async def get_lecture_content(module_id: str, db: AsyncSession = Depends(get_db)):
    # lecture_id = int(lecture_id)
    module_id  = int(module_id)
    try:
        contents = await get_lecture_content_by_module(module_id,db)
        return contents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.get("/courses/lecture/content/{lecture_id}", response_model=dict)
async def get_video_lecture_content(lecture_id: str, db: AsyncSession = Depends(get_db)):
    lecture_id = int(lecture_id)
    try:
        content = await get_lecture_content_by_lecture(lecture_id, db)
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@course_router.post("/courses/module/content/lecture", response_model=dict)
async def add_content(content: LectureContentData, db: AsyncSession = Depends(get_db)):
    """
    Adds a new lecture content to the module of a course
    """
    content_added = await add_lecture_content_to_existing_course(content, db)
    return content_added

@course_router.post("/courses/module", status_code=201)
async def create_module(module_data: ModuleCreate, db: AsyncSession = Depends(get_db)):
    """
    Adds a new module to the course
    """
    new_module = await add_module(module_data, db)
    return new_module

@course_router.put("/courses/module/content/lecture", response_model=dict)
async def update_content(content: UpdateLectureContentData, db: AsyncSession = Depends(get_db)):
    """
    Updates an existing lecture content in the module of a course
    """
    updated_content = await update_existing_lecture_content(content, db)
    return updated_content




@course_router.delete("/courses/module/{module_id}")
async def delete_module(module_id: str, db: AsyncSession = Depends(get_db)):
    """
    Deletes a module from the course
    """
    try:
        module_id = int(module_id)
        deleted = await delete_module_by_id(module_id, db)
        if deleted:
            return {"message": "Module deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Module not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.post("/courses", response_model=dict)
async def create_course(course_data: CourseCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new course
    """
    try:
        # Create new course object
        new_course = Course(
            name=course_data.name,
            code=course_data.code,
            title=course_data.title,
            credits=course_data.credits,
            duration=course_data.duration,
            semester=course_data.semester,
            year=course_data.year,
            faculty_id=course_data.faculty_id,
            created_by=course_data.created_by,
            syllabus=course_data.syllabus,
            description=course_data.description,
            status=CourseStatus.DRAFT
        )
        
        # Add to database
        db.add(new_course)
        await db.commit()
        await db.refresh(new_course)
        
        return new_course.to_dict()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



