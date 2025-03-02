from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Body, Path
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.assignment import Assignment, Submission
from app.services.assignment_service import AssignmentService
from app.services.auth_service import get_current_user, get_current_faculty
from typing import List, Optional
import uuid
import os
import json
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["assignments"])

# Pydantic models for request/response validation
class AssignmentCreate(BaseModel):
    """
    Model for creating a new assignment.
    """
    title: str = Field(..., description="Assignment title")
    description: str = Field(..., description="Detailed description of the assignment")
    course_id: uuid.UUID = Field(..., description="ID of the course this assignment belongs to")
    module_id: Optional[uuid.UUID] = Field(None, description="Optional ID of the module this assignment belongs to")
    due_date: datetime = Field(..., description="Deadline for assignment submission")
    points: int = Field(0, description="Maximum points possible for this assignment")
    status: str = Field("draft", description="Assignment status (draft, published, archived)")
    submission_type: str = Field("file", description="Type of submission (file, text, url, media)")
    allow_late_submissions: bool = Field(False, description="Whether late submissions are allowed")
    late_penalty: float = Field(0, description="Percentage penalty per day for late submissions")
    group_submission: bool = Field(False, description="Whether group submissions are allowed")
    max_group_size: int = Field(1, description="Maximum number of students in a group")
    enable_peer_review: bool = Field(False, description="Whether peer review is enabled")
    peer_reviewers_count: int = Field(0, description="Number of peer reviewers per submission")
    peer_review_due_date: Optional[datetime] = Field(None, description="Deadline for peer reviews")
    plagiarism_detection: bool = Field(True, description="Whether plagiarism detection is enabled")
    file_types: str = Field("pdf,doc,docx,txt", description="Comma-separated list of allowed file types")
    max_file_size: int = Field(10, description="Maximum file size in MB")
    settings: Optional[dict] = Field(None, description="Additional settings as JSON")

class AssignmentUpdate(BaseModel):
    """
    Model for updating an existing assignment.
    """
    title: Optional[str] = Field(None, description="Assignment title")
    description: Optional[str] = Field(None, description="Detailed description of the assignment")
    due_date: Optional[datetime] = Field(None, description="Deadline for assignment submission")
    points: Optional[int] = Field(None, description="Maximum points possible for this assignment")
    status: Optional[str] = Field(None, description="Assignment status (draft, published, archived)")
    submission_type: Optional[str] = Field(None, description="Type of submission (file, text, url, media)")
    allow_late_submissions: Optional[bool] = Field(None, description="Whether late submissions are allowed")
    late_penalty: Optional[float] = Field(None, description="Percentage penalty per day for late submissions")
    group_submission: Optional[bool] = Field(None, description="Whether group submissions are allowed")
    max_group_size: Optional[int] = Field(None, description="Maximum number of students in a group")
    enable_peer_review: Optional[bool] = Field(None, description="Whether peer review is enabled")
    peer_reviewers_count: Optional[int] = Field(None, description="Number of peer reviewers per submission")
    peer_review_due_date: Optional[datetime] = Field(None, description="Deadline for peer reviews")
    plagiarism_detection: Optional[bool] = Field(None, description="Whether plagiarism detection is enabled")
    file_types: Optional[str] = Field(None, description="Comma-separated list of allowed file types")
    max_file_size: Optional[int] = Field(None, description="Maximum file size in MB")
    settings: Optional[dict] = Field(None, description="Additional settings as JSON")

class SubmissionCreate(BaseModel):
    """
    Model for creating a new submission.
    """
    content: Optional[str] = Field(None, description="Text content of the submission (for text submissions)")
    url: Optional[str] = Field(None, description="URL for the submission (for url submissions)")
    status: str = Field("draft", description="Submission status (draft, submitted)")

class GradeSubmission(BaseModel):
    """
    Model for grading a submission.
    """
    grade: float = Field(..., description="Numeric grade assigned to the submission")
    feedback: Optional[str] = Field(None, description="Feedback text from the instructor")

# Assignment endpoints
@router.post("/assignments", response_model=dict, summary="Create a new assignment", 
             description="Create a new assignment for a course. Only faculty members can create assignments.")
async def create_assignment(
    assignment: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_faculty)
):
    """
    Create a new assignment.
    
    This endpoint allows faculty to create a new assignment for a course.
    
    - **assignment**: Assignment data including title, description, due date, etc.
    
    Returns:
    - **message**: Success message
    - **assignment_id**: ID of the created assignment
    """
    try:
        assignment_data = assignment.dict()
        result = await AssignmentService.create_assignment(db, assignment_data, current_user["id"])
        
        return {
            "message": "Assignment created successfully",
            "assignment_id": str(result.id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assignments", response_model=List[dict], summary="Get all assignments for a course",
            description="Get all assignments for a specified course. Course ID is required as a query parameter.")
async def get_assignments(
    course_id: Optional[uuid.UUID] = Query(None, description="ID of the course to get assignments for"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all assignments.
    
    This endpoint allows users to get all assignments for a course.
    If course_id is provided, only assignments for that course are returned.
    
    - **course_id**: ID of the course to get assignments for (required)
    
    Returns:
    - List of assignment objects with all details
    """
    try:
        if course_id:
            assignments = await AssignmentService.get_assignments_by_course(db, course_id)
        else:
            # In a real system, you would implement logic to get assignments
            # based on the user's role and permissions
            raise HTTPException(status_code=400, detail="Course ID is required")
        
        return [
            {
                "id": str(assignment.id),
                "title": assignment.title,
                "description": assignment.description,
                "course_id": str(assignment.course_id),
                "module_id": str(assignment.module_id) if assignment.module_id else None,
                "created_by": str(assignment.created_by),
                "created_at": assignment.created_at.isoformat(),
                "updated_at": assignment.updated_at.isoformat(),
                "due_date": assignment.due_date.isoformat(),
                "points": assignment.points,
                "status": assignment.status,
                "submission_type": assignment.submission_type,
                "allow_late_submissions": assignment.allow_late_submissions,
                "late_penalty": assignment.late_penalty,
                "group_submission": assignment.group_submission,
                "max_group_size": assignment.max_group_size,
                "enable_peer_review": assignment.enable_peer_review,
                "peer_reviewers_count": assignment.peer_reviewers_count,
                "peer_review_due_date": assignment.peer_review_due_date.isoformat() if assignment.peer_review_due_date else None,
                "plagiarism_detection": assignment.plagiarism_detection,
                "file_types": assignment.file_types,
                "max_file_size": assignment.max_file_size,
                "settings": assignment.settings
            }
            for assignment in assignments
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assignments/{assignment_id}", response_model=dict, summary="Get assignment details",
            description="Get detailed information about a specific assignment by its ID.")
async def get_assignment(
    assignment_id: uuid.UUID = Path(..., description="ID of the assignment to retrieve"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get an assignment by ID.
    
    This endpoint allows users to get an assignment by its ID.
    
    - **assignment_id**: ID of the assignment to retrieve
    
    Returns:
    - Assignment object with all details
    """
    try:
        assignment = await AssignmentService.get_assignment(db, assignment_id)
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        return {
            "id": str(assignment.id),
            "title": assignment.title,
            "description": assignment.description,
            "course_id": str(assignment.course_id),
            "module_id": str(assignment.module_id) if assignment.module_id else None,
            "created_by": str(assignment.created_by),
            "created_at": assignment.created_at.isoformat(),
            "updated_at": assignment.updated_at.isoformat(),
            "due_date": assignment.due_date.isoformat(),
            "points": assignment.points,
            "status": assignment.status,
            "submission_type": assignment.submission_type,
            "allow_late_submissions": assignment.allow_late_submissions,
            "late_penalty": assignment.late_penalty,
            "group_submission": assignment.group_submission,
            "max_group_size": assignment.max_group_size,
            "enable_peer_review": assignment.enable_peer_review,
            "peer_reviewers_count": assignment.peer_reviewers_count,
            "peer_review_due_date": assignment.peer_review_due_date.isoformat() if assignment.peer_review_due_date else None,
            "plagiarism_detection": assignment.plagiarism_detection,
            "file_types": assignment.file_types,
            "max_file_size": assignment.max_file_size,
            "settings": assignment.settings
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/assignments/{assignment_id}", response_model=dict, summary="Update an assignment",
            description="Update an existing assignment. Only faculty members can update assignments.")
async def update_assignment(
    assignment_id: uuid.UUID = Path(..., description="ID of the assignment to update"),
    assignment: AssignmentUpdate = Body(..., description="Updated assignment data"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_faculty)
):
    """
    Update an assignment.
    
    This endpoint allows faculty to update an assignment.
    
    - **assignment_id**: ID of the assignment to update
    - **assignment**: Updated assignment data
    
    Returns:
    - **message**: Success message
    - **assignment_id**: ID of the updated assignment
    """
    try:
        assignment_data = {k: v for k, v in assignment.dict().items() if v is not None}
        result = await AssignmentService.update_assignment(db, assignment_id, assignment_data)
        
        return {
            "message": "Assignment updated successfully",
            "assignment_id": str(result.id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/assignments/{assignment_id}", response_model=dict, summary="Delete an assignment",
               description="Delete an existing assignment. Only faculty members can delete assignments.")
async def delete_assignment(
    assignment_id: uuid.UUID = Path(..., description="ID of the assignment to delete"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_faculty)
):
    """
    Delete an assignment.
    
    This endpoint allows faculty to delete an assignment.
    
    - **assignment_id**: ID of the assignment to delete
    
    Returns:
    - **message**: Success message
    """
    try:
        result = await AssignmentService.delete_assignment(db, assignment_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        return {
            "message": "Assignment deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Submission endpoints
@router.post("/assignments/{assignment_id}/submit", response_model=dict, summary="Submit an assignment",
             description="Submit an assignment. Supports file uploads, text entries, and URL submissions.")
async def submit_assignment(
    assignment_id: uuid.UUID = Path(..., description="ID of the assignment to submit"),
    content: Optional[str] = Form(None, description="Text content of the submission (for text submissions)"),
    url: Optional[str] = Form(None, description="URL for the submission (for url submissions)"),
    status: str = Form("submitted", description="Submission status (draft, submitted)"),
    file: Optional[UploadFile] = File(None, description="File to upload (for file submissions)"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Submit an assignment.
    
    This endpoint allows students to submit an assignment.
    
    - **assignment_id**: ID of the assignment to submit
    - **content**: Text content of the submission (for text submissions)
    - **url**: URL for the submission (for url submissions)
    - **status**: Submission status (draft, submitted)
    - **file**: File to upload (for file submissions)
    
    Returns:
    - **message**: Success message
    - **submission_id**: ID of the created/updated submission
    - **status**: Status of the submission
    """
    try:
        # Validate submission based on assignment type
        assignment = await AssignmentService.get_assignment(db, assignment_id)
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        # Check if assignment is published
        if assignment.status != "published":
            raise HTTPException(status_code=400, detail="Assignment is not published")
        
        # Check if assignment is past due date and late submissions are not allowed
        if (
            assignment.due_date < datetime.utcnow() and 
            not assignment.allow_late_submissions and
            status == "submitted"
        ):
            raise HTTPException(status_code=400, detail="Assignment is past due date and late submissions are not allowed")
        
        # Validate submission based on submission type
        if assignment.submission_type == "file" and not file and status == "submitted":
            raise HTTPException(status_code=400, detail="File is required for this assignment")
        elif assignment.submission_type == "text" and not content and status == "submitted":
            raise HTTPException(status_code=400, detail="Text content is required for this assignment")
        elif assignment.submission_type == "url" and not url and status == "submitted":
            raise HTTPException(status_code=400, detail="URL is required for this assignment")
        
        # Create submission data
        submission_data = {
            "content": content,
            "url": url,
            "status": status
        }
        
        # Create or update submission
        result = await AssignmentService.create_submission(
            db, 
            assignment_id, 
            current_user["id"], 
            submission_data,
            file
        )
        
        return {
            "message": f"Assignment {status} successfully",
            "submission_id": str(result.id),
            "status": result.status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assignments/{assignment_id}/submissions", response_model=List[dict], summary="Get all submissions for an assignment",
            description="Get all submissions for a specific assignment. Only faculty members can access this endpoint.")
async def get_submissions(
    assignment_id: uuid.UUID = Path(..., description="ID of the assignment to get submissions for"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_faculty)
):
    """
    Get all submissions for an assignment.
    
    This endpoint allows faculty to get all submissions for an assignment.
    
    - **assignment_id**: ID of the assignment to get submissions for
    
    Returns:
    - List of submission objects with all details
    """
    try:
        submissions = await AssignmentService.get_submissions_by_assignment(db, assignment_id)
        
        return [
            {
                "id": str(submission.id),
                "assignment_id": str(submission.assignment_id),
                "student_id": str(submission.student_id),
                "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
                "updated_at": submission.updated_at.isoformat(),
                "status": submission.status,
                "content": submission.content,
                "file_name": submission.file_name,
                "file_size": submission.file_size,
                "file_type": submission.file_type,
                "url": submission.url,
                "grade": submission.grade,
                "feedback": submission.feedback,
                "graded_by": str(submission.graded_by) if submission.graded_by else None,
                "graded_at": submission.graded_at.isoformat() if submission.graded_at else None,
                "plagiarism_score": submission.plagiarism_score,
                "late_submission": submission.late_submission,
                "late_penalty_applied": submission.late_penalty_applied
            }
            for submission in submissions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assignments/{assignment_id}/my-submission", response_model=dict, summary="Get current user's submission",
            description="Get the current user's submission for a specific assignment.")
async def get_my_submission(
    assignment_id: uuid.UUID = Path(..., description="ID of the assignment to get submission for"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the current user's submission for an assignment.
    
    This endpoint allows students to get their submission for an assignment.
    
    - **assignment_id**: ID of the assignment to get submission for
    
    Returns:
    - **message**: Success message
    - **submission**: Submission object with all details or null if no submission found
    """
    try:
        submission = await AssignmentService.get_student_submission(db, assignment_id, current_user["id"])
        
        if not submission:
            return {
                "message": "No submission found",
                "submission": None
            }
        
        return {
            "message": "Submission found",
            "submission": {
                "id": str(submission.id),
                "assignment_id": str(submission.assignment_id),
                "student_id": str(submission.student_id),
                "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
                "updated_at": submission.updated_at.isoformat(),
                "status": submission.status,
                "content": submission.content,
                "file_name": submission.file_name,
                "file_size": submission.file_size,
                "file_type": submission.file_type,
                "url": submission.url,
                "grade": submission.grade,
                "feedback": submission.feedback,
                "graded_at": submission.graded_at.isoformat() if submission.graded_at else None,
                "late_submission": submission.late_submission,
                "late_penalty_applied": submission.late_penalty_applied
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/assignments/{assignment_id}/grade/{submission_id}", response_model=dict, summary="Grade a submission",
            description="Grade a submission for a specific assignment. Only faculty members can grade submissions.")
async def grade_submission(
    assignment_id: uuid.UUID = Path(..., description="ID of the assignment"),
    submission_id: uuid.UUID = Path(..., description="ID of the submission to grade"),
    grade_data: GradeSubmission = Body(..., description="Grading data including grade and feedback"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_faculty)
):
    """
    Grade a submission.
    
    This endpoint allows faculty to grade a submission.
    
    - **assignment_id**: ID of the assignment
    - **submission_id**: ID of the submission to grade
    - **grade_data**: Grading data including grade and feedback
    
    Returns:
    - **message**: Success message
    - **submission_id**: ID of the graded submission
    - **grade**: Grade assigned to the submission
    """
    try:
        # Validate that the submission belongs to the assignment
        submission = await AssignmentService.get_submission(db, submission_id)
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        if str(submission.assignment_id) != str(assignment_id):
            raise HTTPException(status_code=400, detail="Submission does not belong to this assignment")
        
        # Validate grade
        assignment = await AssignmentService.get_assignment(db, assignment_id)
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        if grade_data.grade < 0 or grade_data.grade > assignment.points:
            raise HTTPException(
                status_code=400, 
                detail=f"Grade must be between 0 and {assignment.points}"
            )
        
        # Grade submission
        result = await AssignmentService.grade_submission(
            db, 
            submission_id, 
            grade_data.dict(), 
            current_user["id"]
        )
        
        return {
            "message": "Submission graded successfully",
            "submission_id": str(result.id),
            "grade": result.grade
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assignments/{assignment_id}/submissions/{submission_id}/download", response_class=FileResponse, 
            summary="Download submission file", description="Download the file for a specific submission.")
async def download_submission_file(
    assignment_id: uuid.UUID = Path(..., description="ID of the assignment"),
    submission_id: uuid.UUID = Path(..., description="ID of the submission to download file from"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the file for a submission.
    
    This endpoint allows users to download the file for a submission.
    Faculty members can download any submission file, while students can only download their own submission files.
    
    - **assignment_id**: ID of the assignment
    - **submission_id**: ID of the submission to download file from
    
    Returns:
    - The file as a download
    """
    try:
        submission = await AssignmentService.get_submission(db, submission_id)
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        if str(submission.assignment_id) != str(assignment_id):
            raise HTTPException(status_code=400, detail="Submission does not belong to this assignment")
        
        # Check if user has permission to access this file
        is_faculty = current_user.get("role") == "faculty"
        is_owner = str(submission.student_id) == str(current_user["id"])
        
        if not (is_faculty or is_owner):
            raise HTTPException(status_code=403, detail="You do not have permission to access this file")
        
        if not submission.file_path:
            raise HTTPException(status_code=404, detail="No file found for this submission")
        
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "uploads",
            submission.file_path
        )
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=submission.file_name,
            media_type=submission.file_type
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assignments/{assignment_id}/submissions/{submission_id}/plagiarism", response_model=dict, 
            summary="Get plagiarism report", description="Get the plagiarism report for a specific submission. Only faculty members can access this endpoint.")
async def get_plagiarism_report(
    assignment_id: uuid.UUID = Path(..., description="ID of the assignment"),
    submission_id: uuid.UUID = Path(..., description="ID of the submission to get plagiarism report for"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_faculty)
):
    """
    Get the plagiarism report for a submission.
    
    This endpoint allows faculty to get the plagiarism report for a submission.
    
    - **assignment_id**: ID of the assignment
    - **submission_id**: ID of the submission to get plagiarism report for
    
    Returns:
    - **message**: Success message
    - **plagiarism_score**: Plagiarism score (0-100)
    - **report**: Detailed plagiarism report
    """
    try:
        submission = await AssignmentService.get_submission(db, submission_id)
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        if str(submission.assignment_id) != str(assignment_id):
            raise HTTPException(status_code=400, detail="Submission does not belong to this assignment")
        
        if submission.plagiarism_report is None:
            return {
                "message": "No plagiarism report available",
                "plagiarism_score": 0,
                "report": {}
            }
        
        return {
            "message": "Plagiarism report retrieved successfully",
            "plagiarism_score": submission.plagiarism_score,
            "report": submission.plagiarism_report
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 