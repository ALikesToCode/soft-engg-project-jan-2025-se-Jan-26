from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.course import Course, CourseEnrollment
from app.models.assignment import Assignment
from app.models.user import User
from uuid import UUID
from typing import List, Dict, Any
from fastapi import HTTPException

class CourseService:
    @staticmethod
    async def get_user_course_history(db: AsyncSession, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Get the course history for a specific user.
        
        Args:
            db: Database session
            user_id: UUID of the user
            
        Returns:
            List of courses with their details
        """
        query = (
            select(Course, CourseEnrollment)
            .join(CourseEnrollment, Course.id == CourseEnrollment.course_id)
            .where(CourseEnrollment.student_id == user_id)
        )
        
        result = await db.execute(query)
        courses = []
        
        for course, enrollment in result:
            courses.append({
                "id": str(course.id),
                "name": course.name,
                "code": course.code,
                "semester": course.semester,
                "status": enrollment.status,
                "grade": enrollment.grade,
                "credits": course.credits
            })
        
        return courses

    @staticmethod
    async def get_course_enrollment(db: AsyncSession, course_id: UUID) -> List[Dict[str, Any]]:
        """
        Get the enrollment list for a specific course.
        
        Args:
            db: Database session
            course_id: UUID of the course
            
        Returns:
            List of enrolled students with their details
        """
        query = (
            select(User, CourseEnrollment)
            .join(CourseEnrollment, User.id == CourseEnrollment.student_id)
            .where(CourseEnrollment.course_id == course_id)
        )
        
        result = await db.execute(query)
        enrollment = []
        
        for user, enrollment_record in result:
            enrollment.append({
                "student_id": str(user.id),
                "name": user.name,
                "email": user.email,
                "enrollment_date": enrollment_record.enrollment_date.isoformat(),
                "status": enrollment_record.status
            })
        
        return enrollment

    @staticmethod
    async def get_all_course_assignments(db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Get all assignments across all courses.
        
        Args:
            db: Database session
            
        Returns:
            List of assignments with their details
        """
        try:
            # Get all assignments with their corresponding courses
            query = (
                select(Assignment, Course)
                .outerjoin(Course, Assignment.course_id == Course.id)
            )
            
            result = await db.execute(query)
            assignments = []
            
            rows = result.fetchall()
            if not rows:
                return []  # Return empty list if no assignments exist
            
            for assignment, course in rows:
                if assignment:  # Only add if we have an assignment
                    assignment_data = {
                        "id": str(assignment.id),
                        "course_id": str(course.id) if course else None,
                        "course_name": course.name if course else "Unknown Course",
                        "title": assignment.title,
                        "description": assignment.description,
                        "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
                        "status": assignment.status,
                        "points": assignment.points,
                        "submission_type": assignment.submission_type,
                        "allow_late_submissions": assignment.allow_late_submissions,
                        "file_types": assignment.file_types
                    }
                    assignments.append(assignment_data)
            
            return assignments
        except Exception as e:
            print(f"Error in get_all_course_assignments: {str(e)}")  # Log the error
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to retrieve course assignments: {str(e)}"
            ) 