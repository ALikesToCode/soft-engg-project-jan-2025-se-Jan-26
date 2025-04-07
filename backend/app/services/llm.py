from typing import Dict, Any
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.course import Lecture, LectureContent, LectureTranscription

logger = logging.getLogger(__name__)

async def prepare_prompt_for_lecture(db: AsyncSession, context_data: Dict[str, Any]) -> str:
    """
    Prepare a context prompt for lecture-specific conversations.
    
    Args:
        db: Database session
        context_data: Contains lectureId and other context information
        
    Returns:
        A formatted string with lecture details and content
    """
    lecture_id = context_data.get("lectureId")
    if not lecture_id:
        return "No lecture context available."
    
    try:
        # Get lecture with its content and course info
        lecture_query = select(Lecture).filter(Lecture.id == lecture_id)
        result = await db.execute(lecture_query)
        lecture = result.scalar_one_or_none()
        
        if not lecture:
            return f"Cannot find lecture with ID {lecture_id}."
        
        # Get lecture content
        content_query = select(LectureContent).filter(LectureContent.lecture_id == lecture_id)
        content_result = await db.execute(content_query)
        lecture_content = content_result.scalar_one_or_none()
        
        # Get lecture transcription if available
        transcription_query = select(LectureTranscription).filter(LectureTranscription.lecture_id == lecture_id)
        transcription_result = await db.execute(transcription_query)
        lecture_transcription = transcription_result.scalar_one_or_none()
        
        # Build context prompt
        context = f"""
        LECTURE: {lecture.title}
        COURSE: {context_data.get('courseName', 'Unknown Course')}
        DESCRIPTION: {lecture.description or 'No description available'}
        """
        
        # Add lecture content if available
        if lecture_content and lecture_content.content:
            # Limit content to avoid token limits
            content_text = lecture_content.content[:3000] + "..." if len(lecture_content.content) > 3000 else lecture_content.content
            context += f"\nCONTENT SUMMARY:\n{content_text}\n"
        
        # Add transcription summary if available
        if lecture_transcription and lecture_transcription.ai_summary:
            context += f"\nLECTURE SUMMARY:\n{lecture_transcription.ai_summary}\n"
        elif lecture_transcription and lecture_transcription.transcription_text:
            # If we have transcript but no summary, add a truncated version of the transcript
            transcript_preview = lecture_transcription.transcription_text[:2000] + "..." if len(lecture_transcription.transcription_text) > 2000 else lecture_transcription.transcription_text
            context += f"\nLECTURE TRANSCRIPT EXCERPT:\n{transcript_preview}\n"
        
        context += "\nAs a teaching assistant for this lecture, provide helpful, accurate, and concise responses to questions about this content."
        
        return context
    except Exception as e:
        logger.error(f"Error preparing lecture context: {str(e)}")
        return "Error retrieving lecture context." 