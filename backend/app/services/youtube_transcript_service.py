from typing import Dict, List, Optional, Any, Union
import logging
import re
import requests
import json
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class YouTubeTranscriptService:
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        # Handle different YouTube URL formats
        youtube_regex = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        
        match = re.match(youtube_regex, url)
        if match:
            return match.group(6)
        
        # Try parsing the URL directly
        try:
            parsed_url = urlparse(url)
            if parsed_url.netloc in ['youtube.com', 'www.youtube.com']:
                query_params = parse_qs(parsed_url.query)
                return query_params.get('v', [None])[0]
            elif parsed_url.netloc == 'youtu.be':
                return parsed_url.path.lstrip('/')
        except Exception as e:
            logger.error(f"Failed to extract video ID: {str(e)}")
        
        return None

    @staticmethod
    async def get_transcript(video_url: str, language: str = 'en') -> Optional[str]:
        """
        Get transcript for YouTube video
        
        Args:
            video_url: YouTube video URL
            language: Language code for transcript (e.g., 'en', 'es')
            
        Returns:
            Transcript text or None if not available
        """
        try:
            video_id = YouTubeTranscriptService.extract_video_id(video_url)
            if not video_id:
                logger.error(f"Could not extract video ID from URL: {video_url}")
                return None
            
            # Try to use the YouTube transcript API service
            # This is a lightweight service that avoids needing to install extra dependencies
            url = f"https://yt-transcript-api.herokuapp.com/api/transcript?video_id={video_id}&language={language}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    # Format the transcript into a readable text
                    transcript_parts = []
                    for item in data.get('transcript', []):
                        text = item.get('text', '')
                        transcript_parts.append(text)
                    
                    return " ".join(transcript_parts)
                elif data.get('error') == 'Transcript not available':
                    logger.warning(f"No transcript available for video: {video_id}")
                    return None
            
            # Fallback to another service if needed
            fallback_url = f"https://ytsubsapi.jerboa.app/api/get_transcript?video_id={video_id}&language={language}"
            fallback_response = requests.get(fallback_url, timeout=30)
            
            if fallback_response.status_code == 200:
                fallback_data = fallback_response.json()
                if isinstance(fallback_data, list):
                    # Format the transcript into a readable text
                    transcript_parts = []
                    for item in fallback_data:
                        text = item.get('text', '')
                        transcript_parts.append(text)
                    
                    return " ".join(transcript_parts)
            
            logger.warning(f"Could not retrieve transcript for video: {video_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting YouTube transcript: {str(e)}")
            return None
            
    @staticmethod
    async def extract_transcript_from_lecture(lecture_url: str) -> Optional[str]:
        """
        Extract transcript from a lecture URL
        
        Args:
            lecture_url: URL of the lecture (YouTube or other)
            
        Returns:
            Transcript text or None if not available
        """
        # Check if it's a YouTube URL
        if 'youtube.com' in lecture_url or 'youtu.be' in lecture_url:
            return await YouTubeTranscriptService.get_transcript(lecture_url)
        
        # For non-YouTube URLs, we would need different approaches
        # This could be a placeholder for future extensions
        logger.warning(f"Non-YouTube URL provided, transcript extraction not supported: {lecture_url}")
        return None 