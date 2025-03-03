import asyncio
from app.database import get_db, Base, engine
from app.models.course import Course, CourseEnrollment, CourseStatus, EnrollmentStatus
from app.models.user import User
from app.models.assignment import Assignment
from sqlalchemy.future import select
import uuid
from datetime import datetime, timedelta

async def create_test_courses():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async for db in get_db():
        # Get faculty user
        faculty = await db.execute(select(User).where(User.email == 'faculty@study.iitm.ac.in'))
        faculty = faculty.scalars().first()
        
        if not faculty:
            print("Faculty user not found. Please run create_test_user.py first.")
            return
            
        # Get student user
        student = await db.execute(select(User).where(User.email == 'student@study.iitm.ac.in'))
        student = student.scalars().first()
        
        if not student:
            print("Student user not found. Please run create_test_user.py first.")
            return
        
        # Create test course
        course = await db.execute(select(Course).where(Course.code == 'CS101'))
        course = course.scalars().first()
        
        if not course:
            course = Course(
                id=uuid.uuid4(),
                name='Introduction to Computer Science',
                code='CS101',
                description='An introductory course to computer science fundamentals',
                credits=3,
                semester='Spring',
                year=2025,
                status=CourseStatus.ACTIVE,
                created_by=faculty.id,
                faculty_id=faculty.id,
                created_at=datetime.now()
            )
            db.add(course)
            await db.commit()
            print(f'Created course: {course.name} with code: {course.code} and id: {course.id}')
        else:
            print(f'Course already exists: {course.name} with code: {course.code} and id: {course.id}')
        
        # Enroll student in course
        enrollment = await db.execute(
            select(CourseEnrollment)
            .where(CourseEnrollment.course_id == course.id)
            .where(CourseEnrollment.student_id == student.id)
        )
        enrollment = enrollment.scalars().first()
        
        if not enrollment:
            enrollment = CourseEnrollment(
                id=uuid.uuid4(),
                course_id=course.id,
                student_id=student.id,
                status=EnrollmentStatus.ENROLLED,
                enrollment_date=datetime.now(),
                created_at=datetime.now()
            )
            db.add(enrollment)
            await db.commit()
            print(f'Enrolled student {student.email} in course {course.code}')
        else:
            print(f'Student {student.email} already enrolled in course {course.code}')
        
        # Create test assignments
        assignments = [
            {
                'title': 'Introduction to Python',
                'description': 'Learn the basics of Python programming language',
                'due_date': datetime.now() + timedelta(days=7),
                'points': 100,
                'status': 'published'
            },
            {
                'title': 'Data Structures',
                'description': 'Implement basic data structures in Python',
                'due_date': datetime.now() + timedelta(days=14),
                'points': 150,
                'status': 'published'
            },
            {
                'title': 'Algorithms',
                'description': 'Implement sorting and searching algorithms',
                'due_date': datetime.now() + timedelta(days=21),
                'points': 200,
                'status': 'draft'
            }
        ]
        
        for assignment_data in assignments:
            # Check if assignment already exists
            existing_assignment = await db.execute(
                select(Assignment)
                .where(Assignment.course_id == course.id)
                .where(Assignment.title == assignment_data['title'])
            )
            existing_assignment = existing_assignment.scalars().first()
            
            if not existing_assignment:
                assignment = Assignment(
                    id=uuid.uuid4(),
                    course_id=course.id,
                    created_by=faculty.id,
                    created_at=datetime.now(),
                    submission_type='file',
                    allow_late_submissions=True,
                    late_penalty=10,
                    file_types='pdf,doc,docx,txt',
                    max_file_size=10,
                    **assignment_data
                )
                db.add(assignment)
                await db.commit()
                print(f'Created assignment: {assignment.title} for course {course.code}')
            else:
                print(f'Assignment {assignment_data["title"]} already exists for course {course.code}')
        
        break  # Exit after first iteration

if __name__ == "__main__":
    asyncio.run(create_test_courses()) 