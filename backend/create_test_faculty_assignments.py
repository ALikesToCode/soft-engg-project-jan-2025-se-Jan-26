import asyncio
import os
import sys
from random import randint
from uuid import UUID

# Add project directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import async_session
from app.models.course import Course
from app.models.user import User
from sqlalchemy import select, update

async def create_test_faculty_assignments():
    """Create test faculty assignments"""
    print("Creating test faculty assignments...")
    
    async with async_session() as session:
        # Get all courses
        result = await session.execute(select(Course))
        courses = result.scalars().all()
        
        if not courses:
            print("No courses found. Creating test courses first...")
            try:
                from create_test_data import create_test_course
                await create_test_course()
                
                # Query again after creating test courses
                result = await session.execute(select(Course))
                courses = result.scalars().all()
            except ImportError:
                print("Failed to import create_test_course. Please run create_test_data.py first.")
                return
            
        # Get faculty members
        result = await session.execute(
            select(User).filter(User.roles.any(name="faculty"))
        )
        faculty = result.scalars().all()
        
        if not faculty:
            print("No faculty members found. Make sure there are users with faculty role.")
            return
        
        print(f"Found {len(courses)} courses and {len(faculty)} faculty members")
        
        # Assign faculty to courses in a rotating fashion
        faculty_index = 0
        for course in courses:
            # Skip courses that already have faculty assigned
            if course.faculty_id is not None:
                continue
                
            # Assign faculty
            course.faculty_id = faculty[faculty_index].id
            
            # Set capacity and enrolled count
            course.capacity = randint(30, 100)
            
            # We'll just set a random enrolled count for testing
            # In a real system, this would be calculated from actual enrollments
            course.enrolled_count = randint(0, course.capacity)
            
            # Move to next faculty member
            faculty_index = (faculty_index + 1) % len(faculty)
        
        # Commit changes
        await session.commit()
        print("Created test faculty assignments successfully")

async def main():
    try:
        await create_test_faculty_assignments()
        print("Completed test data generation")
    except Exception as e:
        print(f"Error creating test faculty assignments: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 