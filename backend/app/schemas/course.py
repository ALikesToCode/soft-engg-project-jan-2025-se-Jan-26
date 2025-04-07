from typing import List, Optional, Dict, Any
from pydantic import BaseModel, UUID4, validator, HttpUrl
from datetime import datetime
from enum import Enum

# ... rest of the schemas

# Lecture Transcription Schemas
class LectureTranscriptionBase(BaseModel):
    transcription_text: str
    ai_summary: Optional[str] = None

class LectureTranscriptionCreate(LectureTranscriptionBase):
    lecture_id: int

class LectureTranscriptionUpdate(BaseModel):
    transcription_text: Optional[str] = None
    ai_summary: Optional[str] = None
    processed: Optional[bool] = None

class LectureTranscription(LectureTranscriptionBase):
    id: int
    lecture_id: int
    created_at: datetime
    updated_at: datetime
    processed: bool
    
    class Config:
        orm_mode = True

# AI Summary Generation Schema
class SummaryRequest(BaseModel):
    lecture_id: int
    max_length: Optional[int] = 500

class SummaryResponse(BaseModel):
    lecture_id: int
    summary: str
    created_at: datetime 