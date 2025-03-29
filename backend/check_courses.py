import asyncio
import os
import logging
from dotenv import load_dotenv
import psycopg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

async def check_courses():
    """Check if there are any courses in the database"""
    # Load environment variables
    load_dotenv()
    
    # Get connection string
    connection_string = os.getenv("DATABASE_URL")
    if not connection_string:
        logger.error("DATABASE_URL environment variable is not set")
        return False
    
    # Ensure sslmode=require is present
    if "sslmode=require" not in connection_string:
        if "?" in connection_string:
            connection_string += "&sslmode=require"
        else:
            connection_string += "?sslmode=require"
    
    # Convert SQLAlchemy URL format to psycopg format if needed
    if "postgresql+asyncpg://" in connection_string:
        connection_string = connection_string.replace("postgresql+asyncpg://", "postgresql://")
    
    logger.info(f"Connecting to database...")
    
    try:
        # Connect to the database
        conn = await psycopg.AsyncConnection.connect(connection_string)
        
        # Check if the courses table exists
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT EXISTS (
                   SELECT FROM information_schema.tables 
                   WHERE table_schema = 'public'
                   AND table_name = 'courses'
                );
            """)
            result = await cur.fetchone()
            table_exists = result[0]
            
            if not table_exists:
                logger.info("The courses table does not exist.")
                await conn.close()
                return False
            
            # Query for courses
            await cur.execute("SELECT COUNT(*) FROM courses;")
            count = await cur.fetchone()
            logger.info(f"Found {count[0]} courses in the database.")
            
            # Show course details if there are any
            if count[0] > 0:
                await cur.execute("""
                    SELECT id, title, description, created_at, updated_at, status 
                    FROM courses 
                    LIMIT 10;
                """)
                courses = await cur.fetchall()
                logger.info("Course details:")
                for course in courses:
                    logger.info(f"ID: {course[0]}, Title: {course[1]}, Status: {course[5]}")
            
        # Close the connection
        await conn.close()
        logger.info("Database connection closed.")
        return True
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Checking courses in the database...")
    asyncio.run(check_courses()) 