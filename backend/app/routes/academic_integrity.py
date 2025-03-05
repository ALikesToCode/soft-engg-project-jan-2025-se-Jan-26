from fastapi import APIRouter, Depends, HTTPException, status, Request, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from app.database import get_db, AsyncSession
from app.services.auth_service import require_auth, require_role
import logging
import json
import re
import uuid
from enum import Enum

router = APIRouter(
    prefix="/academic-integrity",
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
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
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
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "reviewed_by": user.get('sub'),
            "comments": [
                {
                    "user_id": user.get('sub'),
                    "comment": update_data.comment,
                    "timestamp": datetime.now()
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
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "reviewed_by": user.get('sub'),
            "comments": [
                {
                    "user_id": user.get('sub'),
                    "comment": f"Escalated: {escalation_details.reason}",
                    "timestamp": datetime.now()
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
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
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
                "timestamp": datetime.now(),
                "details": {"severity": "medium", "source": "assignment"}
            },
            {
                "id": str(uuid.uuid4()),
                "flag_id": flag_id,
                "action": "update",
                "user_id": "faculty_456",
                "timestamp": datetime.now(),
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