import os
import json
import logging
from typing import Dict, Any, Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GeminiIntegrityService:
    """
    Service for checking LLM responses with Google's Gemini to detect academic integrity issues.
    
    This service uses Gemini to analyze LLM responses and flag any potential academic integrity concerns.
    """
    
    def __init__(self):
        """Initialize the Gemini integrity checker service."""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not found in environment variables")
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Initialize Gemini model for integrity checking
        try:
            self.gemini = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                google_api_key=self.api_key,
                temperature=0
            )
            logger.info("Gemini integrity checker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise
    
    async def check_integrity(
        self, 
        llm_response: str, 
        original_query: Optional[str] = None, 
        course_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check the integrity of an LLM response using Gemini.
        
        Args:
            llm_response: The LLM response to check
            original_query: The original user query that generated the response
            course_context: Optional context about the course or assignment
            
        Returns:
            Dictionary containing the integrity analysis results
        """
        try:
            # Construct the prompt for Gemini
            system_prompt = self._build_integrity_prompt()
            
            # Prepare input data
            input_data = {
                "response": llm_response
            }
            
            if original_query:
                input_data["query"] = original_query
                
            if course_context:
                input_data["context"] = course_context
            
            # Format the input for Gemini
            formatted_input = json.dumps(input_data, indent=2)
            
            # Send to Gemini
            response = await self.gemini.ainvoke(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": formatted_input}
                ]
            )
            
            # Parse and validate the response
            try:
                result = self._parse_integrity_response(response.content)
                logger.info(f"Integrity check completed with score: {result.get('integrity_score', 'N/A')}")
                return result
            except Exception as parse_error:
                logger.error(f"Failed to parse Gemini response: {str(parse_error)}")
                return self._fallback_response(str(parse_error))
                
        except Exception as e:
            logger.error(f"Error in integrity check: {str(e)}")
            return self._fallback_response(str(e))
    
    def _build_integrity_prompt(self) -> str:
        """
        Build the system prompt for Gemini to analyze academic integrity issues.
        
        Returns:
            A string containing the system prompt for Gemini
        """
        return """You are AcademicGuardian, an expert system for detecting academic integrity violations in AI-generated content. Your task is to analyze responses from LLM systems and identify potential academic integrity issues.

INPUT: 
- The complete text of an LLM response to a student query
- The original student query (if available)
- Course context (if available)

ANALYSIS STEPS:
1. Read the entire response carefully
2. Look for these specific violations:
   - Direct plagiarism (exact copying without attribution)
   - Solution provision (providing complete answers rather than guidance)
   - Code completion (writing full code solutions for assignments)
   - Exam answer generation
   - Citation fabrication (creating fake references)
   - Mathematical solution bypassing (solving problems without showing work)

OUTPUT FORMAT:
{
  "flagged": true/false,
  "integrity_score": 0-100,
  "analysis": {
    "summary": "Brief overall assessment",
    "flags": [
      {
        "type": "violation_type",
        "severity": "high/medium/low",
        "explanation": "Why this is problematic",
        "location": {
          "start_index": position_number,
          "end_index": position_number
        },
        "text": "The exact problematic text",
        "recommendation": "How to address this issue"
      }
    ]
  }
}

IMPORTANT GUIDELINES:
- Focus on academic integrity issues, not writing quality or factual accuracy
- Be specific about WHY something violates academic integrity
- Provide actionable recommendations for each flag
- Maintain balanced judgment - not all assistance is academic dishonesty
- Distinguish between guidance (acceptable) and solution provision (problematic)
- Consider educational context - different standards apply for different levels
- Pay special attention to code solutions, mathematical answers, and direct quotes
- Assign severity based on how significantly the content undermines learning objectives

When analyzing code:
- Look for comments indicating it's a complete solution
- Check if code includes detailed explanations or is just raw solution
- Assess if code is templated guidance or complete implementation

For mathematical problems:
- Determine if steps are explained or just answers provided
- Check for educational value versus shortcut delivery

YOUR RESPONSE MUST BE VALID JSON that can be parsed by JavaScript frontend applications.
"""
    
    def _parse_integrity_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse and validate the Gemini response.
        
        Args:
            response_text: The raw text response from Gemini
            
        Returns:
            Parsed JSON response as a dictionary
            
        Raises:
            ValueError: If response cannot be parsed as valid JSON
        """
        # Extract JSON if it's wrapped in ```json and ``` tags
        if "```json" in response_text and "```" in response_text.split("```json", 1)[1]:
            json_text = response_text.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in response_text and "```" in response_text.split("```", 1)[1]:
            json_text = response_text.split("```", 1)[1].split("```", 1)[0].strip()
        else:
            json_text = response_text.strip()
        
        try:
            # Parse JSON
            result = json.loads(json_text)
            
            # Validate required fields
            if "flagged" not in result:
                raise ValueError("Response missing 'flagged' field")
                
            if "integrity_score" not in result:
                result["integrity_score"] = 100 if not result["flagged"] else 50
                
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {str(e)}")
            raise ValueError(f"Invalid JSON in Gemini response: {str(e)}")
    
    def _fallback_response(self, error_message: str) -> Dict[str, Any]:
        """
        Generate a fallback response when integrity checking fails.
        
        Args:
            error_message: The error message explaining the failure
            
        Returns:
            A fallback integrity analysis response
        """
        return {
            "flagged": False,
            "integrity_score": 100,
            "analysis": {
                "summary": "Integrity check could not be completed",
                "flags": [],
                "error": error_message
            }
        }


# Create a singleton instance
gemini_integrity_service = GeminiIntegrityService() 