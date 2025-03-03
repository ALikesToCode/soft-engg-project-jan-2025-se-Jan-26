from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.course import Course, Module, LectureContent, Lecture
from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from app.utils.content_type import ContentType

async def get_all_courses(db: AsyncSession):
    result = await db.execute(select(Course))
    courses = result.scalars().all()  # Fetch all course objects
    return [courses.to_dict() for courses in courses] 


async def get_modules_by_course(course_id: str, db: AsyncSession):
    result = await db.execute(
        select(Module).where(Module.course_id == course_id).order_by(Module.position)
    )
    modules = result.scalars().all()  
    return [module.to_dict() for module in modules]

async def get_lecture_for_module(module_id: int, db: AsyncSession):
    result = await db.execute(select(Lecture).where(Lecture.module_id == module_id))
    lectures = result.scalars().all()  
    return [lecture.to_dict() for lecture in lectures]

async def get_lecture_content_by_module(module_id: int, db: AsyncSession):
    result = await db.execute(
        select(Lecture)
        .options(joinedload(Lecture.contents))  # Eager load contents
        .where(Lecture.module_id == module_id)
    )
    lectures = result.scalars().unique().all() 
    if not lectures:
        raise HTTPException(status_code=404, detail="No lectures found for the given module")

    # Flatten contents from lectures
    contents = [content for lecture in lectures for content in lecture.contents]

    return [content.to_dict() for content in contents]

async def get_lecture_content_by_lecture(lecture_id: int, db: AsyncSession):
    try:
        result = await db.execute(select(LectureContent).where(LectureContent.lecture_id == lecture_id))
        content = result.scalars().first() 
        if not content:
            raise HTTPException(status_code=404, detail="No content found for the given lecture")
        return content.to_dict()
    except Exception as e:
        print(f"Error fetching course content: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def add_lecture_content_to_existing_course(content,db: AsyncSession):
    try:
        # Check if course exists
        course = await db.execute(select(Course).where(Course.id == int(content.courseId)))
        course = course.scalars().first()

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")


        # Check if module exists
        module = await db.execute(select(Module).where(Module.id == int(content.moduleId)))
        module = module.scalars().first()

        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        lectures = await db.execute(
            select(Lecture)
            .where(Lecture.module_id == int(content.moduleId))
            .order_by(Lecture.position.desc())  # Sorting in descending order
            .limit(1)  # Fetch only the top row
        )

        first_lecture = lectures.scalars().first()
        position = 1 if not first_lecture else first_lecture.position + 1

        content_type = "lecture"
        if(content.type == "quiz"):
            content_type = ContentType.QUIZ
        elif(content.type == "assignment"):
            content_type = ContentType.ASSIGNMENT
        elif(content.type == "document"):
            content_type = ContentType.DOCUMENT

        new_lecture = Lecture(
            module_id=int(content.moduleId),
            content_type=content_type,
            position=position,
        )

        db.add(new_lecture)
        await db.commit()
        await db.refresh(new_lecture)

        new_lecture_content = LectureContent(
            lecture_id=new_lecture.id,
            title=content.title,
            content_url=content.videoUrl,
            content_desc=content.description,
        )
        db.add(new_lecture_content)
        await db.commit()
        await db.refresh(new_lecture_content)
        return {"message": "Content added successfully"}
    
    except Exception as e:
        await db.rollback()  # Rollback if error occurs
        raise HTTPException(status_code=500, detail=str(e))

async def add_doc_content_to_existing_course(content,db: AsyncSession):
    pass

async def update_existing_lecture_content(content,db: AsyncSession):
    try:
        lecture_id = int(content.lectureId)
        result = await db.execute(
        select(Lecture)
        .join(LectureContent, Lecture.id == LectureContent.lecture_id)
        .where(LectureContent.id == lecture_id)
        )
        lecture = result.scalars().first()

        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        if lecture.content_type != content.type:
            raise HTTPException(status_code=400, detail="Content type cannot be changed")

        # Check if LectureContent exists
        lecture_content = await db.execute(select(LectureContent).where(LectureContent.id == int(lecture_id)))
        lecture_content = lecture_content.scalars().first()

        if not lecture_content:
            raise HTTPException(status_code=404, detail="LectureContent not found")
        
        #update the content
        try:
            lecture_content.title = content.title
            lecture_content.content_url = content.videoUrl
            lecture_content.content_desc = content.description
            await db.commit()
            return {"message": "Content added successfully"}
        except Exception as e:
            await db.rollback()  
            raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        print("Error updating content2: ", str(e))
        await db.rollback()  # Rollback if error occurs
        raise HTTPException(status_code=500, detail=str(e))


async def add_module(module_data, db: AsyncSession):
    try:
        new_module = Module(
            course_id=int(module_data.course_id),
            title=module_data.title,
            position=module_data.position,
        )
        
        db.add(new_module)
        await db.commit()
        await db.refresh(new_module)
        
        return new_module
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def delete_module_by_id(module_id: int, db: AsyncSession):
    try:
        result = await db.execute(select(Module).filter(Module.id == module_id))
        module = result.scalars().first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        await db.delete(module)
        await db.commit()
        return {"message": "Module deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise e  # Re-raise exception for proper error handling
