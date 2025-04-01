from fastapi import APIRouter, Depends, HTTPException, status, Request, Path, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, UTC
from app.database import get_db, AsyncSession
from app.services.auth_service import require_auth, require_role, get_current_faculty, get_current_user
import logging
import json
import re
import uuid
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from app.models.assignment import Submission
from app.models.user import User
from app.services.gemini_integrity_service import gemini_integrity_service

router = APIRouter(
    tags=["academic-integrity"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

# Add a simple test endpoint
@router.get("/test")
async def test_endpoint():
    return {"message": "Academic integrity router is working!"}

# Models for academic integrity flags
class FlagStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"
    ESCALATED = "escalated"
    RESOLVED = "resolved"

class FlagCreate(BaseModel):
    """Model for creating a new academic integrity flag"""
    content: str = Field(..., description="The content that triggered the flag")
    context: Dict[str, Any] = Field(..., description="Context information about the flagged content")
    source: str = Field(..., description="Source of the flagged content (e.g., 'assignment', 'chat')")
    severity: str = Field(..., description="Severity level of the flag (e.g., 'low', 'medium', 'high')")
    course_id: Optional[str] = Field(None, description="ID of the course if applicable")
    user_id: str = Field(..., description="ID of the user who created the content")

class FlagUpdate(BaseModel):
    """Model for updating an academic integrity flag"""
    status: FlagStatus = Field(..., description="New status for the flag")
    comment: Optional[str] = Field(None, description="Comment explaining the status update")

class EscalationDetails(BaseModel):
    """Model for escalating an academic integrity flag"""
    reason: str = Field(..., description="Reason for escalation")
    escalate_to: List[str] = Field(..., description="IDs of users to escalate to")
    priority: str = Field(..., description="Priority of the escalation (e.g., 'low', 'medium', 'high')")
    additional_notes: Optional[str] = Field(None, description="Additional notes for the escalation")

class FlagResponse(BaseModel):
    """Response model for academic integrity flags"""
    id: str = Field(..., description="Unique identifier for the flag")
    content: str = Field(..., description="The content that triggered the flag")
    context: Dict[str, Any] = Field(..., description="Context information about the flagged content")
    source: str = Field(..., description="Source of the flagged content")
    severity: str = Field(..., description="Severity level of the flag")
    status: FlagStatus = Field(..., description="Current status of the flag")
    course_id: Optional[str] = Field(None, description="ID of the course if applicable")
    user_id: str = Field(..., description="ID of the user who created the content")
    created_at: datetime = Field(..., description="Timestamp when the flag was created")
    updated_at: datetime = Field(..., description="Timestamp when the flag was last updated")
    reviewed_by: Optional[str] = Field(None, description="ID of the user who reviewed the flag")
    comments: List[Dict[str, Any]] = Field(default=[], description="Comments on the flag")

class FlagStatistics(BaseModel):
    """Response model for flag statistics"""
    total_flags: int = Field(..., description="Total number of flags")
    by_status: Dict[str, int] = Field(..., description="Flags grouped by status")
    by_severity: Dict[str, int] = Field(..., description="Flags grouped by severity")
    by_source: Dict[str, int] = Field(..., description="Flags grouped by source")
    recent_flags: List[FlagResponse] = Field(..., description="Most recent flags")
    course_id: Optional[str] = Field(None, description="ID of the course if applicable")

class AuditEntry(BaseModel):
    """Model for an audit trail entry"""
    id: str = Field(..., description="Unique identifier for the audit entry")
    flag_id: str = Field(..., description="ID of the flag this audit entry is for")
    action: str = Field(..., description="Action performed (e.g., 'create', 'update', 'escalate')")
    user_id: str = Field(..., description="ID of the user who performed the action")
    timestamp: datetime = Field(..., description="Timestamp when the action was performed")
    details: Dict[str, Any] = Field(..., description="Details of the action")

class LLMRequestValidationModel(BaseModel):
    """
    Model for validating LLM requests for academic integrity concerns.
    """
    content: str = Field(..., description="The content of the LLM request to validate")

class ValidationResponse(BaseModel):
    """
    Response model for LLM request validation.
    """
    isValid: bool = Field(..., description="Whether the request is valid or not")
    reason: Optional[str] = Field(None, description="Reason for validation result")
    containsSensitiveContent: bool = Field(..., description="Whether the request contains sensitive content")
    sensitiveContentDetails: Optional[Dict[str, Any]] = Field(None, description="Details about the sensitive content")

# Schema for academic integrity flag
class AcademicIntegrityFlag(BaseModel):
    """
    Model for academic integrity flag.
    """
    id: uuid.UUID = Field(..., description="Unique ID for the flag")
    submission_id: uuid.UUID = Field(..., description="ID of the flagged submission")
    assignment_id: uuid.UUID = Field(..., description="ID of the assignment")
    student_id: uuid.UUID = Field(..., description="ID of the student whose submission is flagged")
    flagged_by: uuid.UUID = Field(..., description="ID of the faculty who flagged the submission")
    reason: str = Field(..., description="Reason for flagging the submission")
    status: str = Field(..., description="Status of the flag (pending, resolved, dismissed)")
    resolution_notes: Optional[str] = Field(None, description="Notes on how the flag was resolved")
    created_at: datetime = Field(..., description="Timestamp when the flag was created")
    updated_at: datetime = Field(..., description="Timestamp when the flag was last updated")

# Schema for creating a new flag
class AcademicIntegrityFlagCreate(BaseModel):
    """
    Model for creating a new academic integrity flag.
    """
    reason: str = Field(..., description="Reason for flagging the submission")
    status: str = Field("pending", description="Status of the flag (pending, resolved, dismissed)")

# Schema for updating a flag
class AcademicIntegrityFlagUpdate(BaseModel):
    """
    Model for updating an academic integrity flag.
    """
    reason: Optional[str] = Field(None, description="Reason for flagging the submission")
    status: Optional[str] = Field(None, description="Status of the flag (pending, resolved, dismissed)")
    resolution_notes: Optional[str] = Field(None, description="Notes on how the flag was resolved")

# Get all flagged interactions
@router.get("/flags", 
    response_model=List[FlagResponse],
    summary="Get all flagged interactions",
    description="Retrieves all flagged interactions with optional filtering",
    response_description="List of academic integrity flags"
)
async def get_flagged_interactions(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    source: Optional[str] = Query(None, description="Filter by source"),
    course_id: Optional[str] = Query(None, description="Filter by course ID"),
    limit: int = Query(50, description="Maximum number of flags to return"),
    offset: int = Query(0, description="Number of flags to skip")
):
    """
    Get all flagged interactions with optional filtering.
    
    This endpoint allows faculty and administrators to retrieve academic integrity flags
    with various filtering options.
    """
    try:
        logger.info(f"Getting flagged interactions for user {user.get('sub')}")
        
        # Mock data for demonstration purposes
        # In a real implementation, this would query the database
        flags = [
            {
                "id": str(uuid.uuid4()),
                "content": "Sample flagged content",
                "context": {"assignment_id": "123", "submission_id": "456"},
                "source": "assignment",
                "severity": "medium",
                "status": "pending",
                "course_id": "course_123",
                "user_id": "user_789",
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
                "reviewed_by": None,
                "comments": []
            }
        ]
        
        return flags
        
    except Exception as e:
        logger.error(f"Error getting flagged interactions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving flagged interactions"
        )

# Update flag status
@router.put("/flags/{flag_id}", 
    response_model=FlagResponse,
    summary="Update flag status",
    description="Updates the status of an academic integrity flag",
    response_description="Updated flag information"
)
async def update_flag_status(
    request: Request,
    update_data: FlagUpdate,
    flag_id: str = Path(..., description="ID of the flag to update"),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Update the status of an academic integrity flag.
    
    This endpoint allows faculty and administrators to update the status of a flag
    and add comments explaining the update.
    """
    try:
        logger.info(f"Updating flag {flag_id} by user {user.get('sub')}")
        
        # Mock data for demonstration purposes
        # In a real implementation, this would update the database
        updated_flag = {
            "id": flag_id,
            "content": "Sample flagged content",
            "context": {"assignment_id": "123", "submission_id": "456"},
            "source": "assignment",
            "severity": "medium",
            "status": update_data.status,
            "course_id": "course_123",
            "user_id": "user_789",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "reviewed_by": user.get('sub'),
            "comments": [
                {
                    "user_id": user.get('sub'),
                    "comment": update_data.comment,
                    "timestamp": datetime.now(UTC)
                }
            ]
        }
        
        return updated_flag
        
    except Exception as e:
        logger.error(f"Error updating flag status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating flag status"
        )

# Escalate a flagged item
@router.post("/flags/{flag_id}/escalate", 
    response_model=FlagResponse,
    summary="Escalate a flagged item",
    description="Escalates an academic integrity flag to specified users",
    response_description="Updated flag information after escalation"
)
async def escalate_flag(
    request: Request,
    escalation_details: EscalationDetails,
    flag_id: str = Path(..., description="ID of the flag to escalate"),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Escalate an academic integrity flag to specified users.
    
    This endpoint allows faculty to escalate a flag to administrators or other faculty
    members for further review.
    """
    try:
        logger.info(f"Escalating flag {flag_id} by user {user.get('sub')}")
        
        # Mock data for demonstration purposes
        # In a real implementation, this would update the database and notify users
        escalated_flag = {
            "id": flag_id,
            "content": "Sample flagged content",
            "context": {"assignment_id": "123", "submission_id": "456"},
            "source": "assignment",
            "severity": "high",  # Increased severity due to escalation
            "status": "escalated",
            "course_id": "course_123",
            "user_id": "user_789",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "reviewed_by": user.get('sub'),
            "comments": [
                {
                    "user_id": user.get('sub'),
                    "comment": f"Escalated: {escalation_details.reason}",
                    "timestamp": datetime.now(UTC)
                }
            ]
        }
        
        return escalated_flag
        
    except Exception as e:
        logger.error(f"Error escalating flag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error escalating flag"
        )

# Get flag statistics
@router.get("/statistics/{course_id}", 
    response_model=FlagStatistics,
    summary="Get flag statistics",
    description="Retrieves statistics about academic integrity flags for a course",
    response_description="Flag statistics for the specified course"
)
async def get_flag_statistics(
    request: Request,
    course_id: str = Path(..., description="ID of the course to get statistics for"),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Get statistics about academic integrity flags for a course.
    
    This endpoint provides aggregated data about flags, including counts by status,
    severity, and source, as well as recent flags.
    """
    try:
        logger.info(f"Getting flag statistics for course {course_id} by user {user.get('sub')}")
        
        # Mock data for demonstration purposes
        # In a real implementation, this would query the database for statistics
        statistics = {
            "total_flags": 10,
            "by_status": {
                "pending": 3,
                "reviewed": 2,
                "dismissed": 1,
                "escalated": 2,
                "resolved": 2
            },
            "by_severity": {
                "low": 2,
                "medium": 5,
                "high": 3
            },
            "by_source": {
                "assignment": 6,
                "chat": 4
            },
            "recent_flags": [
                {
                    "id": str(uuid.uuid4()),
                    "content": "Recent flagged content",
                    "context": {"assignment_id": "123", "submission_id": "456"},
                    "source": "assignment",
                    "severity": "medium",
                    "status": "pending",
                    "course_id": course_id,
                    "user_id": "user_789",
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC),
                    "reviewed_by": None,
                    "comments": []
                }
            ],
            "course_id": course_id
        }
        
        return statistics
        
    except Exception as e:
        logger.error(f"Error getting flag statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving flag statistics"
        )

# Get audit trail for a flag
@router.get("/flags/{flag_id}/audit", 
    response_model=List[AuditEntry],
    summary="Get audit trail for a flag",
    description="Retrieves the audit trail for an academic integrity flag",
    response_description="Audit trail entries for the specified flag"
)
async def get_flag_audit_trail(
    request: Request,
    flag_id: str = Path(..., description="ID of the flag to get audit trail for"),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """
    Get the audit trail for an academic integrity flag.
    
    This endpoint provides a chronological history of actions performed on a flag,
    including creation, status updates, and escalations.
    """
    try:
        logger.info(f"Getting audit trail for flag {flag_id} by user {user.get('sub')}")
        
        # Mock data for demonstration purposes
        # In a real implementation, this would query the database for audit entries
        audit_trail = [
            {
                "id": str(uuid.uuid4()),
                "flag_id": flag_id,
                "action": "create",
                "user_id": "user_123",
                "timestamp": datetime.now(UTC),
                "details": {"severity": "medium", "source": "assignment"}
            },
            {
                "id": str(uuid.uuid4()),
                "flag_id": flag_id,
                "action": "update",
                "user_id": "faculty_456",
                "timestamp": datetime.now(UTC),
                "details": {"status": "reviewed", "comment": "Reviewing this flag"}
            }
        ]
        
        return audit_trail
        
    except Exception as e:
        logger.error(f"Error getting flag audit trail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving flag audit trail"
        )

@router.post("/validate-llm-request")
async def validate_llm_request(request: LLMRequestValidationModel, user: dict = Depends(require_auth)):
    """
    Validate an LLM request for academic integrity concerns.
    """
    logging.info(f"User {user.get('sub')} requested LLM validation for content: {request.content[:50]}...")
    try:
        # Get the content to validate
        content = request.content.lower()
        
        # Define patterns for sensitive content
        sensitive_patterns = [
            r"(answer|solution)\s+(key|sheet)",
            r"(exam|test|quiz)\s+(answer|solution)",
            r"(grade|grading)\s+(curve|scale|rubric)",
            r"(cheat|plagiari[sz]e|plagiarism)",
            r"academic\s+(integrity|dishonesty)",
            r"(assignment|homework)\s+(answer|solution)",
            r"(exam|test)\s+question",
            r"(grade|score|mark)\s+(distribution|average)",
            r"(student|peer)\s+(grade|performance|score)",
            r"(answer|solve)\s+(for|my)\s+(assignment|homework|exam|quiz)"
        ]
        
        # Check for sensitive patterns
        matches = []
        for pattern in sensitive_patterns:
            if re.search(pattern, content):
                matches.append(pattern)
        
        # Determine if the request is valid
        is_valid = len(matches) == 0
        
        # Prepare the response
        response = {
            "isValid": is_valid,
            "containsSensitiveContent": not is_valid,
            "sensitiveContentDetails": None
        }
        
        if not is_valid:
            response["reason"] = "Request may reveal sensitive academic information"
            response["sensitiveContentDetails"] = {
                "matchedPatterns": matches,
                "recommendation": "Please rephrase your request to avoid asking about sensitive academic content"
            }
        else:
            response["reason"] = "No sensitive content detected"
        
        return response
        
    except Exception as e:
        logger.error(f"Error validating LLM request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating LLM request"
        )

@router.post("/assignments/{assignment_id}/submissions/{submission_id}/flag", 
             response_model=dict, summary="Flag a submission for academic integrity concerns")
async def flag_submission(
    assignment_id: uuid.UUID = Path(..., description="ID of the assignment"),
    submission_id: uuid.UUID = Path(..., description="ID of the submission to flag"),
    flag_data: AcademicIntegrityFlagCreate = Body(..., description="Flag data"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_faculty)
):
    """
    Flag a submission for academic integrity concerns.
    
    This endpoint allows faculty to flag a submission for academic integrity concerns such as plagiarism.
    
    - **assignment_id**: ID of the assignment
    - **submission_id**: ID of the submission to flag
    - **flag_data**: Flag data including reason and status
    
    Returns:
    - **message**: Success message
    - **flag_id**: ID of the created flag
    """
    try:
        # Check if submission exists
        submission = await db.get(Submission, submission_id)
        if not submission or submission.assignment_id != assignment_id:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Create flag
        flag = {
            "id": uuid.uuid4(),
            "submission_id": submission_id,
            "assignment_id": assignment_id,
            "student_id": submission.student_id,
            "flagged_by": current_user["id"],
            "reason": flag_data.reason,
            "status": flag_data.status,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        
        # TODO: Store flag in database
        
        return {
            "message": "Submission flagged successfully",
            "flag_id": str(flag["id"])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assignments/{assignment_id}/submissions/{submission_id}/flag", 
            response_model=dict, summary="Get flag for a submission")
async def get_submission_flag(
    assignment_id: uuid.UUID = Path(..., description="ID of the assignment"),
    submission_id: uuid.UUID = Path(..., description="ID of the submission"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_faculty)
):
    """
    Get flag for a submission.
    
    This endpoint allows faculty to get the academic integrity flag for a submission.
    
    - **assignment_id**: ID of the assignment
    - **submission_id**: ID of the submission
    
    Returns:
    - **flag**: Flag data if exists, null otherwise
    """
    try:
        # Check if submission exists
        submission = await db.get(Submission, submission_id)
        if not submission or submission.assignment_id != assignment_id:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # TODO: Get flag from database
        # For now, return mock data
        flag = {
            "id": uuid.uuid4(),
            "submission_id": submission_id,
            "assignment_id": assignment_id,
            "student_id": submission.student_id,
            "flagged_by": current_user["id"],
            "reason": "Suspected plagiarism",
            "status": "pending",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        
        return {
            "flag": flag
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/assignments/{assignment_id}/submissions/{submission_id}/flag", 
            response_model=dict, summary="Update flag for a submission")
async def update_submission_flag(
    assignment_id: uuid.UUID = Path(..., description="ID of the assignment"),
    submission_id: uuid.UUID = Path(..., description="ID of the submission"),
    flag_data: AcademicIntegrityFlagUpdate = Body(..., description="Updated flag data"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_faculty)
):
    """
    Update flag for a submission.
    
    This endpoint allows faculty to update the academic integrity flag for a submission.
    
    - **assignment_id**: ID of the assignment
    - **submission_id**: ID of the submission
    - **flag_data**: Updated flag data
    
    Returns:
    - **message**: Success message
    - **flag**: Updated flag data
    """
    try:
        # Check if submission exists
        submission = await db.get(Submission, submission_id)
        if not submission or submission.assignment_id != assignment_id:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # TODO: Update flag in database
        # For now, return mock data
        flag = {
            "id": uuid.uuid4(),
            "submission_id": submission_id,
            "assignment_id": assignment_id,
            "student_id": submission.student_id,
            "flagged_by": current_user["id"],
            "reason": flag_data.reason or "Suspected plagiarism",
            "status": flag_data.status or "pending",
            "resolution_notes": flag_data.resolution_notes,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        
        return {
            "message": "Flag updated successfully",
            "flag": flag
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/flags", response_model=List[dict], summary="Get all academic integrity flags")
async def get_all_flags(
    status: Optional[str] = Query(None, description="Filter flags by status"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_faculty)
):
    """
    Get all academic integrity flags.
    
    This endpoint allows faculty to get all academic integrity flags, optionally filtered by status.
    
    - **status**: Optional filter for flag status (pending, resolved, dismissed)
    
    Returns:
    - **flags**: List of flag data
    """
    try:
        # TODO: Get flags from database
        # For now, return mock data
        flags = [
            {
                "id": uuid.uuid4(),
                "submission_id": uuid.uuid4(),
                "assignment_id": uuid.uuid4(),
                "student_id": uuid.uuid4(),
                "flagged_by": current_user["id"],
                "reason": "Suspected plagiarism",
                "status": "pending",
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        ]
        
        # Filter by status if provided
        if status:
            flags = [f for f in flags if f["status"] == status]
        
        return flags
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Schema for checking LLM responses for academic integrity
class LLMResponseCheckRequest(BaseModel):
    """
    Model for checking LLM responses for academic integrity issues.
    """
    response: str = Field(..., description="The LLM response to check")
    query: Optional[str] = Field(None, description="The original query that generated the response")
    course_context: Optional[str] = Field(None, description="Course context information")

class LLMResponseCheckResponse(BaseModel):
    """
    Response model for LLM response integrity check.
    """
    flagged: bool = Field(..., description="Whether the response was flagged for integrity issues")
    integrity_score: int = Field(..., description="Integrity score (0-100)")
    analysis: Dict[str, Any] = Field(..., description="Detailed analysis of the response")

# Endpoint for checking LLM responses
@router.post("/check-llm-response", 
    response_model=LLMResponseCheckResponse,
    summary="Check LLM response for academic integrity issues",
    description="Analyzes an LLM response for potential academic integrity violations",
    response_description="Academic integrity analysis results",
    responses={
        200: {
            "description": "Analysis completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "flagged": True,
                        "integrity_score": 65,
                        "analysis": {
                            "summary": "Response contains potential academic integrity issues",
                            "flags": [
                                {
                                    "type": "solution_provision",
                                    "severity": "medium",
                                    "explanation": "Provides a complete solution without requiring student work",
                                    "location": {
                                        "start_index": 120,
                                        "end_index": 340
                                    },
                                    "text": "Here's the complete solution to your assignment...",
                                    "recommendation": "Provide guidance on approach rather than complete solution"
                                }
                            ]
                        }
                    }
                }
            }
        },
        400: {
            "description": "Bad request - Invalid input",
            "content": {
                "application/json": {
                    "example": {"detail": "Response text is too short for analysis"}
                }
            }
        },
        500: {
            "description": "Server error during analysis",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to analyze response"}
                }
            }
        }
    }
)
async def check_llm_response(
    request: LLMResponseCheckRequest,
    current_user: dict = Depends(get_current_faculty)
):
    """
    Check an LLM response for academic integrity issues.
    
    This endpoint uses Google's Gemini model to analyze an LLM response for potential
    academic integrity violations such as plagiarism, solution provision, or code completion.
    
    Args:
        request: The LLM response check request
        current_user: The authenticated faculty user
        
    Returns:
        Analysis results including flagged status, integrity score, and detailed explanation
        
    Raises:
        HTTPException: If the analysis fails or the input is invalid
    """
    try:
        logger.info(f"Faculty {current_user.get('email')} requested LLM response integrity check")
        
        # Validate input
        if len(request.response) < 10:
            raise HTTPException(status_code=400, detail="Response text is too short for analysis")
            
        # Get analysis from Gemini service
        analysis_result = await gemini_integrity_service.check_integrity(
            llm_response=request.response,
            original_query=request.query,
            course_context=request.course_context
        )
        
        # Log the result
        is_flagged = analysis_result.get("flagged", False)
        integrity_score = analysis_result.get("integrity_score", 0)
        logger.info(f"LLM response analyzed with score {integrity_score}, flagged: {is_flagged}")
        
        # Return the analysis results
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing LLM response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze response: {str(e)}"
        ) 