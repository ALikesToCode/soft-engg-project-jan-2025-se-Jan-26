#AddCourseContent Request schema
from pydantic import BaseModel
from typing import List, Optional

class LectureContentCreate(BaseModel):
    title: str
    content_url: str
    content_type: str
    # content_desc: Optional[str] = None

class LectureCreate(BaseModel):
    position: int
    contents: List[LectureContentCreate] = []

class ModuleCreate(BaseModel):
    title: str
    position: int
    lectures: List[LectureCreate] = []

class AddCourseContent(BaseModel):
    course_id: int
    modules: List[ModuleCreate] = []


class ModuleCreate(BaseModel):
    course_id: str
    title: str
    position: int


class Metadata(BaseModel):
    duration: Optional[str] = ''
    difficulty: Optional[str] = 'intermediate'
    prerequisites: List[str] = []
    learningObjectives: List[str] = []
    visibility: Optional[str] = 'hidden'

class LectureContentData(BaseModel):
    courseId: str
    moduleId: str
    lectureId: str
    title: str
    description: str
    type: str
    videoUrl: str
    status: str
    order: int
    metadata: Metadata

class UpdateLectureContentData(BaseModel):
    moduleId : str
    lectureId: str
    title: str
    description: str
    type: str
    videoUrl: str
    status: str
    order: int
    metadata: Metadata

"""
{
    "course_id": 1,
    "modules": [
        {
            "title": "Week 3: Object-Oriented Programming",
            "position": 3,
            "lectures": [
                {
                    "position": 1,
                    "contents": [
                        {
                            "title": "Introduction to OOP",
                            "content_url": "https://youtube.com/oop_intro",
                            "content_type": "video",
                            "content_desc": "A detailed explanation of Object-Oriented Programming."
                        }
                    ]
                }
            ]
        }
    ]
}

"""