import asyncio
import logging
from sqlalchemy import text

# Configure minimal logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_imports():
    """Test importing key modules without errors"""
    try:
        # Import the database components
        from app.database import async_session_maker, init_db, engine
        logger.info("Database components imported successfully")
        
        # Import the models
        from app.models.user import User
        from app.models.course import Course, user_courses
        logger.info("Models imported successfully")
        
        # Import app config
        from app.config import settings
        logger.info("Config imported successfully")
        
        # Simple database connection test
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            assert value == 1
            logger.info("Database connection test successful")
            
        logger.info("All imports and tests completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Error during import test: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_imports())
    if result:
        print("All tests passed!")
    else:
        print("Tests failed. See logs for details.")
        exit(1) 