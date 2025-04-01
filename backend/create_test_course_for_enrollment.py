#!/usr/bin/env python3
import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import text

from app.database import get_db, Base, engine
from app.models.course import Course, CourseEnrollment, CourseStatus, EnrollmentStatus
from app.models.user import User

# The hardcoded UUID from test_enrollment_api.py
TEST_COURSE_ID = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")

async def create_test_course():
    """Create a test course with the specific UUID for testing."""
    async for db in get_db():
        try:
            # Check if we already have a faculty user
            faculty_query = text("""
                SELECT * FROM users WHERE role = 'faculty' LIMIT 1
            """)
            result = await db.execute(faculty_query)
            faculty = result.first()
            
            if not faculty:
                # Create a faculty user if none exists
                faculty_user = User(
                    name="Test Faculty",
                    email="faculty@test.com",
                    password="facultypassword",  # This would be hashed in a real system
                    role="faculty"
                )
                db.add(faculty_user)
                await db.commit()
                faculty_id = faculty_user.id
            else:
                faculty_id = faculty.id
                
            # Check if course with this ID already exists
            course_query = text("""
                SELECT * FROM courses WHERE id = :course_id
            """)
            result = await db.execute(course_query, {"course_id": TEST_COURSE_ID})
            existing_course = result.first()
            
            if existing_course:
                print(f"Test course with ID {TEST_COURSE_ID} already exists")
                return
            
            # Create course with the specific UUID
            test_course = Course(
                id=TEST_COURSE_ID,
                name="Test Course",
                code="TEST101",
                title="Test Course for Enrollment API",
                description="This course is used for testing the enrollment API",
                credits=3,
                duration=12,
                semester="Spring",
                year=2025,
                status=CourseStatus.ACTIVE,
                faculty_id=faculty_id,
                created_by=faculty_id
            )
            
            db.add(test_course)
            await db.commit()
            print(f"Created test course with ID: {TEST_COURSE_ID}")
            
            # Check if we have student users
            student_query = text("""
                SELECT * FROM users WHERE role = 'student' LIMIT 5
            """)
            result = await db.execute(student_query)
            students = result.fetchall()
            
            if not students:
                # Create a test student
                test_student = User(
                    name="Test Student",
                    email="student@test.com",
                    password="studentpassword",  # This would be hashed in a real system
                    role="student"
                )
                db.add(test_student)
                await db.commit()
                student_id = test_student.id
                students = [(student_id,)]
            
            # Create enrollments for test students
            for student in students:
                student_id = student[0]
                
                # Check if enrollment already exists
                enroll_query = text("""
                    SELECT * FROM course_enrollments 
                    WHERE course_id = :course_id AND student_id = :student_id
                """)
                result = await db.execute(
                    enroll_query, 
                    {"course_id": TEST_COURSE_ID, "student_id": student_id}
                )
                existing_enrollment = result.first()
                
                if existing_enrollment:
                    print(f"Student {student_id} already enrolled in test course")
                    continue
                
                enrollment = CourseEnrollment(
                    course_id=TEST_COURSE_ID,
                    student_id=student_id,
                    user_id=faculty_id,  # Faculty created the enrollment
                    status=EnrollmentStatus.ENROLLED.value,
                    enrollment_date=datetime.now(timezone.utc)
                )
                db.add(enrollment)
            
            await db.commit()
            print("Created test enrollments for test course")
            
        except Exception as e:
            print(f"Error creating test course: {str(e)}")
            await db.rollback()
            raise

async def main():
    await create_test_course()

if __name__ == "__main__":
    asyncio.run(main()) 