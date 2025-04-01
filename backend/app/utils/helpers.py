#AddCourseContent Request schema
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import uuid

class LectureContentCreate(BaseModel):
    title: str
    content_url: str
    content_type: str
    # content_desc: Optional[str] = None

class LectureCreate(BaseModel):
    position: int
    contents: List[LectureContentCreate] = []

class ModuleCreate(BaseModel):
    course_id: str
    title: str
    position: int

class AddCourseContent(BaseModel):
    course_id: int
    modules: List[ModuleCreate] = []


class Metadata(BaseModel):
    duration: Optional[str] = ''
    difficulty: Optional[str] = 'intermediate'
    prerequisites: List[str] = []
    learningObjectives: List[str] = []
    visibility: Optional[str] = 'hidden'

class LectureContentData(BaseModel):
    courseId: str
    moduleId: str
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


class DocumentLinkCreate(BaseModel):
    courseId: uuid.UUID
    moduleId: str
    title: str
    description: Optional[str] = None
    order: int
    status: str
    type: str
    videoUrl: Optional[str] = None
    metadata: Metadata
    driveDocLink: HttpUrl


class UpdateDocumentLinkCreate(BaseModel):
    courseId: uuid.UUID
    moduleId: str
    lectureId: str
    title: str
    description: Optional[str] = None
    order: int
    status: str
    type: str
    videoUrl: Optional[str] = None
    metadata: Metadata
    driveDocLink: HttpUrl
