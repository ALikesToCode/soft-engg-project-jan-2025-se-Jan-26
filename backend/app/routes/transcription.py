from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.transcript_service import TranscriptService
from app.services.youtube_transcript_service import YouTubeTranscriptService
from app.schemas.course import (
    LectureTranscription, 
    LectureTranscriptionCreate, 
    LectureTranscriptionUpdate, 
    SummaryRequest,
    SummaryResponse
)
from app.models.course import Lecture, LectureContent

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "/{lecture_id}",
    response_model=LectureTranscription,
    summary="Get lecture transcription",
    description="Retrieve the transcription for a specific lecture."
)
async def get_lecture_transcript(
    lecture_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get transcription for a lecture"""
    transcript = await TranscriptService.get_lecture_transcript(db, lecture_id)
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found"
        )
    return transcript

@router.post(
    "/",
    response_model=LectureTranscription,
    status_code=status.HTTP_201_CREATED,
    summary="Create lecture transcription",
    description="Create a new transcription for a lecture."
)
async def create_lecture_transcript(
    transcript_data: LectureTranscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Create a new lecture transcription"""
    # Check if user is authenticated and has appropriate role
    if not current_user or current_user.get("role") not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create transcriptions"
        )
    
    # Check if transcription already exists
    existing = await TranscriptService.get_lecture_transcript(db, transcript_data.lecture_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transcription already exists for this lecture"
        )
    
    # Create the transcription
    transcript = await TranscriptService.create_lecture_transcript(db, transcript_data)
    return transcript

@router.put(
    "/{lecture_id}",
    response_model=LectureTranscription,
    summary="Update lecture transcription",
    description="Update an existing lecture transcription."
)
async def update_lecture_transcript(
    lecture_id: int,
    transcript_data: LectureTranscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Update an existing lecture transcription"""
    # Check if user is authenticated and has appropriate role
    if not current_user or current_user.get("role") not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update transcriptions"
        )
    
    # Update the transcription
    transcript = await TranscriptService.update_lecture_transcript(db, lecture_id, transcript_data)
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found"
        )
    
    return transcript

@router.delete(
    "/{lecture_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete lecture transcription",
    description="Delete a lecture transcription."
)
async def delete_lecture_transcript(
    lecture_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Delete a lecture transcription"""
    # Check if user is authenticated and has appropriate role
    if not current_user or current_user.get("role") not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete transcriptions"
        )
    
    # Delete the transcription
    success = await TranscriptService.delete_lecture_transcript(db, lecture_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found"
        )
    
    return None

@router.post(
    "/extract/{lecture_id}",
    response_model=LectureTranscription,
    summary="Extract transcription from video",
    description="Extract transcription from a lecture video URL (YouTube supported)."
)
async def extract_transcript(
    lecture_id: int,
    language: str = Query("en", description="Language code for transcript (e.g., 'en', 'es')"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Extract transcription from a lecture video"""
    # Check if user is authenticated and has appropriate role
    if not current_user or current_user.get("role") not in ["admin", "instructor", "student"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to extract transcriptions"
        )
    
    # Check if transcription already exists
    existing = await TranscriptService.get_lecture_transcript(db, lecture_id)
    if existing:
        return existing
    
    # Get the lecture details to find the video URL
    from sqlalchemy.future import select
    from sqlalchemy.orm import joinedload
    
    query = select(Lecture).options(
        joinedload(Lecture.contents)
    ).where(Lecture.id == lecture_id)
    
    result = await db.execute(query)
    lecture = result.scalars().first()
    
    if not lecture or not lecture.contents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lecture not found or has no content"
        )
    
    # Get the video URL
    video_url = None
    for content in lecture.contents:
        if hasattr(content, 'content_url') and content.content_url:
            # Simple check for video URLs
            if ('youtube.com' in content.content_url or 
                'youtu.be' in content.content_url or 
                'vimeo.com' in content.content_url or
                '.mp4' in content.content_url):
                video_url = content.content_url
                break
    
    if not video_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No video URL found for this lecture"
        )
    
    # Extract transcript from video URL
    transcript_text = await YouTubeTranscriptService.extract_transcript_from_lecture(video_url)
    
    if not transcript_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract transcript from video URL"
        )
    
    # Create a new transcription
    transcript_data = LectureTranscriptionCreate(
        lecture_id=lecture_id,
        transcription_text=transcript_text
    )
    
    # Create the transcription
    transcript = await TranscriptService.create_lecture_transcript(db, transcript_data)
    
    # Generate summary in the background
    background_tasks.add_task(
        generate_summary_background,
        db,
        SummaryRequest(lecture_id=lecture_id)
    )
    
    return transcript

async def generate_summary_background(db: AsyncSession, request: SummaryRequest):
    """Generate summary in the background"""
    try:
        await TranscriptService.generate_ai_summary(db, request)
    except Exception as e:
        logger.error(f"Background summary generation error: {str(e)}")

@router.post(
    "/summary",
    response_model=SummaryResponse,
    summary="Generate AI summary",
    description="Generate an AI summary for a lecture transcription."
)
async def generate_summary(
    request: SummaryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Generate an AI summary for a lecture transcription"""
    # Check if user is authenticated
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Generate summary
    summary = await TranscriptService.generate_ai_summary(db, request)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not generate summary"
        )
    
    return summary 