from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base, UUID
import uuid
from datetime import datetime, UTC

class Assignment(Base):
    """
    Assignment model representing course assignments.
    
    This model stores essential assignment information including title, description,
    due date, and grading settings.
    
    Attributes:
        id: Unique UUID primary key for the assignment
        title: Assignment title
        description: Assignment description
        course_id: Foreign key to the course this assignment belongs to
        module_id: Foreign key to the module this assignment belongs to (optional)
        created_by: Foreign key to the user who created the assignment
        created_at: Timestamp when the assignment was created
        updated_at: Timestamp when the assignment was last updated
        due_date: Deadline for assignment submission
        points: Maximum points possible for this assignment
        status: Assignment status (draft, published, archived)
        submission_type: Type of submission (file, text, url, media)
        allow_late_submissions: Whether late submissions are allowed
        late_penalty: Percentage penalty per day for late submissions
        group_submission: Whether group submissions are allowed
        max_group_size: Maximum number of students in a group
        enable_peer_review: Whether peer review is enabled
        peer_reviewers_count: Number of peer reviewers per submission
        peer_review_due_date: Deadline for peer reviews
        plagiarism_detection: Whether plagiarism detection is enabled
        file_types: Allowed file types for submission
        max_file_size: Maximum file size in MB
        settings: Additional settings as JSON
    """
    __tablename__ = "assignments"

    id = Column(UUID, primary_key=True, default=uuid.uuid4, 
                comment="Unique identifier for the assignment")
    title = Column(String, nullable=False, 
                  comment="Assignment title")
    description = Column(Text, nullable=False, 
                        comment="Assignment description")
    course_id = Column(UUID, ForeignKey("courses.id"), nullable=False, 
                      comment="Foreign key to the course this assignment belongs to")
    module_id = Column(UUID, nullable=True, 
                      comment="Foreign key to the module this assignment belongs to (optional)")
    created_by = Column(UUID, ForeignKey("users.id"), nullable=False, 
                       comment="Foreign key to the user who created the assignment")
    created_at = Column(DateTime, default=datetime.now(UTC), 
                       comment="Timestamp when the assignment was created")
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), 
                       comment="Timestamp when the assignment was last updated")
    due_date = Column(DateTime, nullable=False, 
                     comment="Deadline for assignment submission")
    points = Column(Integer, default=0, 
                   comment="Maximum points possible for this assignment")
    status = Column(String, default="draft", 
                   comment="Assignment status (draft, published, archived)")
    submission_type = Column(String, default="file", 
                            comment="Type of submission (file, text, url, media)")
    allow_late_submissions = Column(Boolean, default=False, 
                                   comment="Whether late submissions are allowed")
    late_penalty = Column(Float, default=0, 
                         comment="Percentage penalty per day for late submissions")
    group_submission = Column(Boolean, default=False, 
                             comment="Whether group submissions are allowed")
    max_group_size = Column(Integer, default=1, 
                           comment="Maximum number of students in a group")
    enable_peer_review = Column(Boolean, default=False, 
                               comment="Whether peer review is enabled")
    peer_reviewers_count = Column(Integer, default=0, 
                                 comment="Number of peer reviewers per submission")
    peer_review_due_date = Column(DateTime, nullable=True, 
                                 comment="Deadline for peer reviews")
    plagiarism_detection = Column(Boolean, default=True, 
                                 comment="Whether plagiarism detection is enabled")
    file_types = Column(String, default="pdf,doc,docx,txt", 
                       comment="Allowed file types for submission")
    max_file_size = Column(Integer, default=10, 
                          comment="Maximum file size in MB")
    settings = Column(JSON, nullable=True, 
                     comment="Additional settings as JSON")

    # Relationships
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    course = relationship("Course", back_populates="assignments")


class Submission(Base):
    """
    Submission model representing student submissions for assignments.
    
    This model stores submission data including files, text content, and grading information.
    
    Attributes:
        id: Unique UUID primary key for the submission
        assignment_id: Foreign key to the assignment this submission is for
        student_id: Foreign key to the student who submitted
        group_id: Foreign key to the group if this is a group submission (optional)
        submitted_at: Timestamp when the submission was made
        updated_at: Timestamp when the submission was last updated
        status: Submission status (draft, submitted, graded)
        content: Text content of the submission (for text submissions)
        file_path: Path to the submitted file (for file submissions)
        file_name: Original filename of the submitted file
        file_size: Size of the submitted file in bytes
        file_type: MIME type of the submitted file
        url: URL for the submission (for url submissions)
        grade: Numeric grade assigned to the submission
        feedback: Feedback text from the instructor
        graded_by: Foreign key to the user who graded the submission
        graded_at: Timestamp when the submission was graded
        plagiarism_score: Plagiarism detection score (0-100)
        plagiarism_report: Detailed plagiarism report
        late_submission: Whether this was submitted after the due date
        late_penalty_applied: Percentage penalty applied for late submission
    """
    __tablename__ = "submissions"

    id = Column(UUID, primary_key=True, default=uuid.uuid4, 
                comment="Unique identifier for the submission")
    assignment_id = Column(UUID, ForeignKey("assignments.id"), nullable=False, 
                          comment="Foreign key to the assignment this submission is for")
    student_id = Column(UUID, ForeignKey("users.id"), nullable=False, 
                       comment="Foreign key to the student who submitted")
    group_id = Column(UUID, nullable=True, 
                     comment="Foreign key to the group if this is a group submission (optional)")
    submitted_at = Column(DateTime, nullable=True, 
                         comment="Timestamp when the submission was made")
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), 
                       comment="Timestamp when the submission was last updated")
    status = Column(String, default="draft", 
                   comment="Submission status (draft, submitted, graded)")
    content = Column(Text, nullable=True, 
                    comment="Text content of the submission (for text submissions)")
    file_path = Column(String, nullable=True, 
                      comment="Path to the submitted file (for file submissions)")
    file_name = Column(String, nullable=True, 
                      comment="Original filename of the submitted file")
    file_size = Column(Integer, nullable=True, 
                      comment="Size of the submitted file in bytes")
    file_type = Column(String, nullable=True, 
                      comment="MIME type of the submitted file")
    url = Column(String, nullable=True, 
                comment="URL for the submission (for url submissions)")
    grade = Column(Float, nullable=True, 
                  comment="Numeric grade assigned to the submission")
    feedback = Column(Text, nullable=True, 
                     comment="Feedback text from the instructor")
    graded_by = Column(UUID, ForeignKey("users.id"), nullable=True, 
                      comment="Foreign key to the user who graded the submission")
    graded_at = Column(DateTime, nullable=True, 
                      comment="Timestamp when the submission was graded")
    plagiarism_score = Column(Float, nullable=True, 
                             comment="Plagiarism detection score (0-100)")
    plagiarism_report = Column(JSON, nullable=True, 
                              comment="Detailed plagiarism report")
    late_submission = Column(Boolean, default=False, 
                            comment="Whether this was submitted after the due date")
    late_penalty_applied = Column(Float, default=0, 
                                 comment="Percentage penalty applied for late submission")

    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", foreign_keys=[student_id])
    grader = relationship("User", foreign_keys=[graded_by]) 