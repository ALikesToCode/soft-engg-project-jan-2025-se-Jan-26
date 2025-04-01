import asyncio
import os
import sys

# Add project directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, async_session
from app.models.course import Course
from app.models.user import User
from sqlalchemy import text

async def migrate_database():
    """Migrate database to add capacity and enrolled_count to courses"""
    print("Starting database migration for faculty assignments...")
    
    # Create a connection to update tables
    async with engine.begin() as conn:
        # Add new columns if they don't exist
        await conn.execute(
            text("ALTER TABLE courses ADD COLUMN IF NOT EXISTS capacity INTEGER DEFAULT 50")
        )
        
        await conn.execute(
            text("ALTER TABLE courses ADD COLUMN IF NOT EXISTS enrolled_count INTEGER DEFAULT 0")
        )
        
        await conn.execute(
            text("ALTER TABLE courses ALTER COLUMN faculty_id DROP NOT NULL")
        )
        
        print("Schema updated successfully.")
    
    # Update existing data
    async with async_session() as session:
        # Set default values for existing courses
        await session.execute(
            text("UPDATE courses SET capacity = 50, enrolled_count = 0 WHERE capacity IS NULL OR enrolled_count IS NULL")
        )
        
        # Calculate actual enrolled_count for each course
        await session.execute(
            text("""
                UPDATE courses c
                SET enrolled_count = (
                    SELECT COUNT(*) 
                    FROM course_enrollments ce 
                    WHERE ce.course_id = c.id
                )
            """)
        )
        
        await session.commit()
        print("Course data updated with enrollment counts.")
    
    print("Migration completed successfully.")

async def main():
    """Main function"""
    try:
        await migrate_database()
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 