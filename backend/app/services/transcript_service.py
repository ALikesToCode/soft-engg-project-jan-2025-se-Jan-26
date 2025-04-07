from typing import Dict, List, Optional, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import update, or_, and_
import json
import re
from datetime import datetime

from app.models.course import Lecture, LectureTranscription
from app.schemas.course import LectureTranscriptionCreate, LectureTranscriptionUpdate, SummaryRequest
from app.services.llm_service import call_llm
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

class TranscriptService:
    @staticmethod
    async def get_lecture_transcript(db: AsyncSession, lecture_id: int) -> Optional[Dict[str, Any]]:
        """Get the transcription for a lecture"""
        query = select(LectureTranscription).where(LectureTranscription.lecture_id == lecture_id)
        result = await db.execute(query)
        transcript = result.scalars().first()
        if transcript:
            return transcript.to_dict()
        return None

    @staticmethod
    async def create_lecture_transcript(
        db: AsyncSession, transcript_data: LectureTranscriptionCreate
    ) -> Dict[str, Any]:
        """Create a new lecture transcription"""
        transcript = LectureTranscription(**transcript_data.dict())
        db.add(transcript)
        await db.commit()
        await db.refresh(transcript)
        return transcript.to_dict()

    @staticmethod
    async def update_lecture_transcript(
        db: AsyncSession, lecture_id: int, transcript_data: LectureTranscriptionUpdate
    ) -> Optional[Dict[str, Any]]:
        """Update an existing lecture transcription"""
        query = select(LectureTranscription).where(LectureTranscription.lecture_id == lecture_id)
        result = await db.execute(query)
        transcript = result.scalars().first()
        
        if not transcript:
            return None
        
        update_data = transcript_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(transcript, key, value)
        
        await db.commit()
        await db.refresh(transcript)
        return transcript.to_dict()

    @staticmethod
    async def generate_ai_summary(
        db: AsyncSession, request: SummaryRequest
    ) -> Optional[Dict[str, Any]]:
        """Generate an AI summary for a lecture transcription"""
        # Get the transcription
        query = select(LectureTranscription).where(LectureTranscription.lecture_id == request.lecture_id)
        result = await db.execute(query)
        transcript = result.scalars().first()
        
        if not transcript:
            logger.error(f"No transcription found for lecture {request.lecture_id}")
            return None
        
        # Get the lecture details for context
        lecture_query = select(Lecture).options(
            joinedload(Lecture.contents)
        ).where(Lecture.id == request.lecture_id)
        lecture_result = await db.execute(lecture_query)
        lecture = lecture_result.scalars().first()
        
        if not lecture:
            logger.error(f"Lecture {request.lecture_id} not found")
            return None
        
        try:
            # Prepare lecture info for context
            lecture_title = lecture.contents[0].title if lecture.contents else f"Lecture {lecture.position}"
            
            # Truncate transcription if it's too long
            transcription_text = transcript.transcription_text
            max_tokens = 6000  # Approximate token limit for context
            if len(transcription_text) > max_tokens * 4:  # Rough character to token ratio
                logger.info(f"Transcription too long, truncating to ~{max_tokens} tokens")
                transcription_text = transcription_text[:max_tokens * 4]
                transcription_text += "... [transcription truncated due to length]"
            
            # Create system prompt for AI
            system_message = SystemMessage(content=f"""
            You are an educational content summarizer. Your job is to create a concise, informative 
            summary of a lecture transcription. Focus on key concepts, main points, and important details.
            
            The summary should be well-structured with sections and bullet points where appropriate.
            Keep the summary to approximately {request.max_length} words.
            """)
            
            # Create human message with lecture context and transcription
            human_message = HumanMessage(content=f"""
            Please summarize the following lecture: "{lecture_title}"
            
            LECTURE TRANSCRIPTION:
            {transcription_text}
            
            Create a comprehensive summary that captures the key points and concepts from this lecture.
            """)
            
            # Call the LLM service
            messages = [system_message, human_message]
            response = await call_llm(messages)
            
            # Extract summary from response
            summary = response.content if hasattr(response, "content") else "Failed to generate summary"
            
            # Update the transcription with the AI summary
            transcript.ai_summary = summary
            transcript.processed = True
            await db.commit()
            await db.refresh(transcript)
            
            return {
                "lecture_id": request.lecture_id,
                "summary": summary,
                "created_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {str(e)}")
            return None

    @staticmethod
    async def delete_lecture_transcript(db: AsyncSession, lecture_id: int) -> bool:
        """Delete a lecture transcription"""
        query = select(LectureTranscription).where(LectureTranscription.lecture_id == lecture_id)
        result = await db.execute(query)
        transcript = result.scalars().first()
        
        if not transcript:
            return False
        
        await db.delete(transcript)
        await db.commit()
        return True 