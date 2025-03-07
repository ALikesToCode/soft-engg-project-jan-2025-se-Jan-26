import os
import uuid
import shutil
from datetime import datetime, timedelta
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from app.models.assignment import Assignment, Submission
from app.config import settings
import difflib
import hashlib
import aiofiles
import mimetypes
import logging
import boto3
from botocore.exceptions import ClientError
import io

logger = logging.getLogger(__name__)

# Define upload directory - check if we're in a read-only environment
READ_ONLY_ENV = os.environ.get("VERCEL") == "1" or os.environ.get("READ_ONLY_FS") == "1"

# S3 Configuration
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_REGION = os.environ.get("S3_REGION", "auto")

# Initialize S3 client
s3_client = None
if READ_ONLY_ENV and S3_ACCESS_KEY and S3_SECRET_KEY and S3_ENDPOINT_URL and S3_BUCKET_NAME:
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION
        )
        logger.info("S3 client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")
        s3_client = None
elif READ_ONLY_ENV:
    logger.error("Running in read-only environment but S3 credentials are missing. File uploads will not work.")

# Define base upload directory
if READ_ONLY_ENV:
    # In Vercel or other read-only environments, we'll use a temporary directory
    # This is just for initialization - actual file operations will be handled differently
    UPLOAD_DIR = "/tmp"
    ASSIGNMENT_DIR = "/tmp"
    logger.warning("Running in read-only filesystem mode. File uploads will use S3 storage.")
else:
    # For local development, use local filesystem
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    if not os.path.exists(UPLOAD_DIR):
        try:
            os.makedirs(UPLOAD_DIR)
        except OSError as e:
            logger.warning(f"Could not create upload directory: {e}")
            UPLOAD_DIR = "/tmp"

    # Define assignment directory
    ASSIGNMENT_DIR = os.path.join(UPLOAD_DIR, "assignments")
    if not os.path.exists(ASSIGNMENT_DIR):
        try:
            os.makedirs(ASSIGNMENT_DIR)
        except OSError as e:
            logger.warning(f"Could not create assignment directory: {e}")
            ASSIGNMENT_DIR = "/tmp"

def get_file_url(file_path: str, expires_in: int = 3600) -> str:
    """
    Generate a URL for accessing a file.
    
    For S3 files, this generates a pre-signed URL that allows temporary access.
    For local files, this returns a local path.
    
    Args:
        file_path: The file path or S3 key
        expires_in: Expiration time in seconds for pre-signed URLs (default: 1 hour)
        
    Returns:
        A URL or path for accessing the file
    """
    if not file_path:
        return None
        
    # Check if this is an S3 path
    if file_path.startswith("s3://"):
        if not s3_client:
            logger.error("S3 client not initialized. Cannot generate pre-signed URL.")
            return None
            
        try:
            # Extract the S3 key from the file path
            s3_path = file_path.replace(f"s3://{S3_BUCKET_NAME}/", "")
            
            # Generate a pre-signed URL
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': S3_BUCKET_NAME,
                    'Key': s3_path
                },
                ExpiresIn=expires_in
            )
            
            return url
        except ClientError as e:
            logger.error(f"Error generating pre-signed URL: {e}")
            return None
    else:
        # For local files, return the path
        # In a real application, you would need to serve these files through an endpoint
        return file_path

class AssignmentService:
    """
    Service for handling assignment-related operations.
    """
    
    @staticmethod
    async def create_assignment(db: AsyncSession, assignment_data: dict, user_id: uuid.UUID):
        """
        Create a new assignment.
        
        Args:
            db: Database session
            assignment_data: Assignment data
            user_id: ID of the user creating the assignment
            
        Returns:
            The created assignment
        """
        assignment = Assignment(**assignment_data, created_by=user_id)
        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)
        return assignment
    
    @staticmethod
    async def get_assignment(db: AsyncSession, assignment_id: uuid.UUID):
        """
        Get an assignment by ID.
        
        Args:
            db: Database session
            assignment_id: Assignment ID
            
        Returns:
            The assignment or None if not found
        """
        result = await db.execute(select(Assignment).filter(Assignment.id == assignment_id))
        return result.scalars().first()
    
    @staticmethod
    async def get_assignments_by_course(db: AsyncSession, course_id: uuid.UUID):
        """
        Get all assignments for a course.
        
        Args:
            db: Database session
            course_id: Course ID
            
        Returns:
            List of assignments
        """
        result = await db.execute(
            select(Assignment)
            .filter(Assignment.course_id == course_id)
            .order_by(Assignment.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def update_assignment(db: AsyncSession, assignment_id: uuid.UUID, assignment_data: dict):
        """
        Update an assignment.
        
        Args:
            db: Database session
            assignment_id: Assignment ID
            assignment_data: Updated assignment data
            
        Returns:
            The updated assignment
        """
        result = await db.execute(select(Assignment).filter(Assignment.id == assignment_id))
        assignment = result.scalars().first()
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        for key, value in assignment_data.items():
            setattr(assignment, key, value)
        
        assignment.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(assignment)
        return assignment
    
    @staticmethod
    async def delete_assignment(db: AsyncSession, assignment_id: uuid.UUID):
        """
        Delete an assignment.
        
        Args:
            db: Database session
            assignment_id: Assignment ID
            
        Returns:
            True if deleted, False otherwise
        """
        result = await db.execute(select(Assignment).filter(Assignment.id == assignment_id))
        assignment = result.scalars().first()
        
        if not assignment:
            return False
        
        # Delete all files associated with this assignment
        if READ_ONLY_ENV and s3_client:
            # Delete files from S3
            try:
                # List all objects with the assignment_id prefix
                prefix = f"assignments/{assignment_id}/"
                response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
                
                if 'Contents' in response:
                    # Create a list of objects to delete
                    objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
                    
                    # Delete the objects
                    s3_client.delete_objects(
                        Bucket=S3_BUCKET_NAME,
                        Delete={'Objects': objects_to_delete}
                    )
                    logger.info(f"Deleted {len(objects_to_delete)} files from S3 for assignment {assignment_id}")
            except ClientError as e:
                logger.error(f"Error deleting assignment files from S3: {e}")
        elif not READ_ONLY_ENV:
            # Delete files from local filesystem
            assignment_upload_dir = os.path.join(ASSIGNMENT_DIR, str(assignment_id))
            if os.path.exists(assignment_upload_dir):
                try:
                    shutil.rmtree(assignment_upload_dir)
                except OSError as e:
                    logger.error(f"Error deleting assignment files: {e}")
        
        await db.delete(assignment)
        await db.commit()
        return True
    
    @staticmethod
    async def save_file(file: UploadFile, assignment_id: uuid.UUID, student_id: uuid.UUID) -> str:
        """
        Save an uploaded file.
        
        Args:
            file: The uploaded file
            assignment_id: Assignment ID
            student_id: Student ID
            
        Returns:
            The file path or identifier
        """
        # Create a unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{student_id}_{uuid.uuid4()}{file_ext}"
        
        if READ_ONLY_ENV:
            # In read-only environments, use S3 storage
            if s3_client:
                try:
                    # Read file content
                    content = await file.read()
                    
                    # Define S3 key (path in the bucket)
                    s3_key = f"assignments/{assignment_id}/{unique_filename}"
                    
                    # Upload to S3
                    s3_client.upload_fileobj(
                        io.BytesIO(content),
                        S3_BUCKET_NAME,
                        s3_key,
                        ExtraArgs={
                            'ContentType': file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
                        }
                    )
                    
                    # Generate a URL or path identifier
                    file_url = f"s3://{S3_BUCKET_NAME}/{s3_key}"
                    logger.info(f"File uploaded to S3: {file_url}")
                    
                    return file_url
                except Exception as e:
                    logger.error(f"Error uploading file to S3: {e}")
                    return f"error/{unique_filename}"
            else:
                logger.warning("S3 client not initialized. Cannot upload file.")
                return f"error/s3-not-initialized/{unique_filename}"
        else:
            # Create directory for this assignment if it doesn't exist
            assignment_dir = os.path.join(ASSIGNMENT_DIR, str(assignment_id))
            if not os.path.exists(assignment_dir):
                try:
                    os.makedirs(assignment_dir)
                except OSError as e:
                    logger.error(f"Could not create assignment directory: {e}")
                    return f"error/{unique_filename}"
            
            file_path = os.path.join(assignment_dir, unique_filename)
            
            # Save the file
            try:
                # Reset file position to beginning
                await file.seek(0)
                
                async with aiofiles.open(file_path, 'wb') as out_file:
                    content = await file.read()
                    await out_file.write(content)
                
                # Return the relative path from the upload directory
                return os.path.relpath(file_path, UPLOAD_DIR)
            except Exception as e:
                logger.error(f"Error saving file: {e}")
                return f"error/{unique_filename}"
    
    @staticmethod
    async def create_submission(
        db: AsyncSession, 
        assignment_id: uuid.UUID, 
        student_id: uuid.UUID, 
        submission_data: dict,
        file: UploadFile = None
    ):
        """
        Create a new submission.
        
        Args:
            db: Database session
            assignment_id: Assignment ID
            student_id: Student ID
            submission_data: Submission data
            file: Optional uploaded file
            
        Returns:
            The created submission
        """
        # Check if assignment exists
        result = await db.execute(select(Assignment).filter(Assignment.id == assignment_id))
        assignment = result.scalars().first()
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        # Check if student already has a submission for this assignment
        result = await db.execute(
            select(Submission).filter(
                and_(
                    Submission.assignment_id == assignment_id,
                    Submission.student_id == student_id
                )
            )
        )
        existing_submission = result.scalars().first()
        
        # If there's an existing submission, update it
        if existing_submission:
            for key, value in submission_data.items():
                setattr(existing_submission, key, value)
            
            # If status is changed to "submitted", set submitted_at
            if submission_data.get("status") == "submitted" and existing_submission.submitted_at is None:
                existing_submission.submitted_at = datetime.utcnow()
                
                # Check if submission is late
                if assignment.due_date and datetime.utcnow() > assignment.due_date:
                    existing_submission.late_submission = True
                    
                    # Apply late penalty if configured
                    if assignment.allow_late_submissions and assignment.late_penalty > 0:
                        days_late = (datetime.utcnow() - assignment.due_date).days
                        if days_late > 0:
                            existing_submission.late_penalty_applied = min(
                                100, assignment.late_penalty * days_late
                            )
            
            # If a new file is uploaded, save it and update file info
            if file:
                # If using S3 and there's an existing file, delete it
                if READ_ONLY_ENV and s3_client and existing_submission.file_path and existing_submission.file_path.startswith("s3://"):
                    try:
                        # Extract the S3 key from the file path
                        s3_path = existing_submission.file_path.replace(f"s3://{S3_BUCKET_NAME}/", "")
                        
                        # Delete the file from S3
                        s3_client.delete_object(
                            Bucket=S3_BUCKET_NAME,
                            Key=s3_path
                        )
                        logger.info(f"Deleted previous file from S3: {s3_path}")
                    except ClientError as e:
                        logger.error(f"Error deleting previous file from S3: {e}")
                # In a non-read-only environment, delete the old file if it exists
                elif not READ_ONLY_ENV and existing_submission.file_path:
                    old_file_path = os.path.join(UPLOAD_DIR, existing_submission.file_path)
                    if os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                        except OSError as e:
                            logger.error(f"Error removing old file: {e}")
                
                # Save new file
                file_path = await AssignmentService.save_file(file, assignment_id, student_id)
                existing_submission.file_path = file_path
                existing_submission.file_name = file.filename
                existing_submission.file_size = file.size
                existing_submission.file_type = file.content_type or mimetypes.guess_type(file.filename)[0]
            
            existing_submission.updated_at = datetime.utcnow()
            
            # Run plagiarism check if enabled and submission is being submitted
            if assignment.plagiarism_detection and submission_data.get("status") == "submitted":
                await AssignmentService.check_plagiarism(db, existing_submission)
            
            await db.commit()
            await db.refresh(existing_submission)
            return existing_submission
        
        # Otherwise, create a new submission
        submission = Submission(
            assignment_id=assignment_id,
            student_id=student_id,
            **submission_data
        )
        
        # If status is "submitted", set submitted_at
        if submission_data.get("status") == "submitted":
            submission.submitted_at = datetime.utcnow()
            
            # Check if submission is late
            if assignment.due_date and datetime.utcnow() > assignment.due_date:
                submission.late_submission = True
                
                # Apply late penalty if configured
                if assignment.allow_late_submissions and assignment.late_penalty > 0:
                    days_late = (datetime.utcnow() - assignment.due_date).days
                    if days_late > 0:
                        submission.late_penalty_applied = min(
                            100, assignment.late_penalty * days_late
                        )
        
        # If a file is uploaded, save it and update file info
        if file:
            file_path = await AssignmentService.save_file(file, assignment_id, student_id)
            submission.file_path = file_path
            submission.file_name = file.filename
            submission.file_size = file.size
            submission.file_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        
        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        
        # Run plagiarism check if enabled and submission is being submitted
        if assignment.plagiarism_detection and submission_data.get("status") == "submitted":
            await AssignmentService.check_plagiarism(db, submission)
            await db.commit()
            await db.refresh(submission)
        
        return submission
    
    @staticmethod
    async def get_submission(db: AsyncSession, submission_id: uuid.UUID):
        """
        Get a submission by ID.
        
        Args:
            db: Database session
            submission_id: Submission ID
            
        Returns:
            The submission or None if not found
        """
        result = await db.execute(select(Submission).filter(Submission.id == submission_id))
        return result.scalars().first()
    
    @staticmethod
    async def get_submissions_by_assignment(db: AsyncSession, assignment_id: uuid.UUID):
        """
        Get all submissions for an assignment.
        
        Args:
            db: Database session
            assignment_id: Assignment ID
            
        Returns:
            List of submissions
        """
        result = await db.execute(
            select(Submission)
            .filter(Submission.assignment_id == assignment_id)
            .order_by(Submission.submitted_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_student_submission(db: AsyncSession, assignment_id: uuid.UUID, student_id: uuid.UUID):
        """
        Get a student's submission for an assignment.
        
        Args:
            db: Database session
            assignment_id: Assignment ID
            student_id: Student ID
            
        Returns:
            The submission or None if not found
        """
        result = await db.execute(
            select(Submission).filter(
                and_(
                    Submission.assignment_id == assignment_id,
                    Submission.student_id == student_id
                )
            )
        )
        return result.scalars().first()
    
    @staticmethod
    async def grade_submission(
        db: AsyncSession, 
        submission_id: uuid.UUID, 
        grade_data: dict, 
        grader_id: uuid.UUID
    ):
        """
        Grade a submission.
        
        Args:
            db: Database session
            submission_id: Submission ID
            grade_data: Grade data
            grader_id: ID of the user grading the submission
            
        Returns:
            The graded submission
        """
        result = await db.execute(select(Submission).filter(Submission.id == submission_id))
        submission = result.scalars().first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Update submission with grade data
        for key, value in grade_data.items():
            setattr(submission, key, value)
        
        submission.status = "graded"
        submission.graded_by = grader_id
        submission.graded_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(submission)
        return submission
    
    @staticmethod
    async def check_plagiarism(db: AsyncSession, submission: Submission):
        """
        Check a submission for plagiarism.
        
        Args:
            db: Database session
            submission: The submission to check
            
        Returns:
            The updated submission with plagiarism score
        """
        # Get all other submissions for this assignment
        result = await db.execute(
            select(Submission).filter(
                and_(
                    Submission.assignment_id == submission.assignment_id,
                    Submission.id != submission.id,
                    Submission.status == "submitted"
                )
            )
        )
        other_submissions = result.scalars().all()
        
        if not other_submissions:
            # No other submissions to compare with
            submission.plagiarism_score = 0
            submission.plagiarism_report = {"message": "No other submissions to compare with"}
            return submission
        
        # For text submissions, use difflib to compare content
        if submission.content:
            highest_similarity = 0
            similar_submissions = []
            
            for other in other_submissions:
                if other.content:
                    # Calculate similarity ratio
                    similarity = difflib.SequenceMatcher(None, submission.content, other.content).ratio() * 100
                    
                    if similarity > highest_similarity:
                        highest_similarity = similarity
                    
                    if similarity > 30:  # Only report if similarity is above 30%
                        similar_submissions.append({
                            "submission_id": str(other.id),
                            "student_id": str(other.student_id),
                            "similarity": round(similarity, 2)
                        })
            
            submission.plagiarism_score = round(highest_similarity, 2)
            submission.plagiarism_report = {
                "similar_submissions": similar_submissions,
                "method": "text_comparison"
            }
        
        # For file submissions, use a simple hash comparison
        # In a real system, you would use a more sophisticated plagiarism detection algorithm
        elif submission.file_path:
            file_path = os.path.join(UPLOAD_DIR, submission.file_path)
            
            if os.path.exists(file_path):
                # Calculate hash of the file
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                # Compare with other submissions
                identical_files = []
                similar_files = []
                
                for other in other_submissions:
                    if other.file_path:
                        other_file_path = os.path.join(UPLOAD_DIR, other.file_path)
                        
                        if os.path.exists(other_file_path):
                            # Calculate hash of the other file
                            with open(other_file_path, 'rb') as f:
                                other_hash = hashlib.md5(f.read()).hexdigest()
                            
                            # Check if files are identical
                            if file_hash == other_hash:
                                identical_files.append({
                                    "submission_id": str(other.id),
                                    "student_id": str(other.student_id),
                                    "similarity": 100
                                })
                            # For non-identical files, we would need a more sophisticated
                            # algorithm to detect similarity. This is just a placeholder.
                            elif submission.file_type and other.file_type and submission.file_type == other.file_type:
                                # For demonstration, we'll just mark files of the same type as potentially similar
                                similar_files.append({
                                    "submission_id": str(other.id),
                                    "student_id": str(other.student_id),
                                    "similarity": 50  # Placeholder similarity score
                                })
                
                if identical_files:
                    submission.plagiarism_score = 100
                    submission.plagiarism_report = {
                        "identical_files": identical_files,
                        "method": "file_hash_comparison"
                    }
                elif similar_files:
                    submission.plagiarism_score = 50  # Placeholder score
                    submission.plagiarism_report = {
                        "similar_files": similar_files,
                        "method": "file_type_comparison"
                    }
                else:
                    submission.plagiarism_score = 0
                    submission.plagiarism_report = {"message": "No similar files found"}
            else:
                submission.plagiarism_score = 0
                submission.plagiarism_report = {"error": "File not found"}
        else:
            submission.plagiarism_score = 0
            submission.plagiarism_report = {"message": "No content or file to check"}
        
        return submission 