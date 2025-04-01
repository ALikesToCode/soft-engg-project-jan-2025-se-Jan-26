import asyncio
import os
import sys
import logging
from dotenv import load_dotenv
import psycopg
from psycopg_pool import AsyncConnectionPool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

async def test_connection():
    """Test direct connection to Neon DB"""
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
    
    # Remove any invalid parameters
    if "&host_type=host" in connection_string:
        connection_string = connection_string.replace("&host_type=host", "")
    
    logger.info(f"Psycopg version: {psycopg.__version__}")
    logger.info(f"Attempting to connect with connection string: {connection_string}")
    
    try:
        # Try direct connection
        logger.info("Testing direct connection...")
        conn = await psycopg.AsyncConnection.connect(connection_string)
        logger.info("Connection successful!")
        
        # Test a simple query
        logger.info("Testing query...")
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1 as test")
            result = await cur.fetchone()
            logger.info(f"Query result: {result}")
        
        # Close connection
        await conn.close()
        logger.info("Connection closed")
        return True
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        return False

async def test_connection_pool():
    """Test connection pool to Neon DB"""
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
    
    # Remove any invalid parameters
    if "&host_type=host" in connection_string:
        connection_string = connection_string.replace("&host_type=host", "")
    
    logger.info(f"Attempting to create connection pool with: {connection_string}")
    
    try:
        # Create connection pool with all parameters in constructor
        # Note: The warning about constructor deprecation is acceptable 
        # since this is a temporary test
        connection_kwargs = {
            "autocommit": True,
            "connect_timeout": 30,
            "sslmode": "require",
            "application_name": "test_connection",
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
        
        pool = AsyncConnectionPool(
            conninfo=connection_string,
            kwargs=connection_kwargs,
            min_size=1,
            max_size=3
        )
        
        # The pool is created during initialization, no need to call open()
        logger.info("Pool created successfully!")
        
        # Test a connection from the pool
        logger.info("Testing connection from pool...")
        async with pool.connection() as conn:
            # Execute a simple query
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1 as test")
                result = await cur.fetchone()
                logger.info(f"Query result: {result}")
        
        # Close the pool
        await pool.close()
        logger.info("Pool closed successfully")
        return True
    except Exception as e:
        logger.error(f"Pool creation failed: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting connection tests...")
    
    result = asyncio.run(test_connection())
    if result:
        logger.info("Direct connection test completed successfully")
    else:
        logger.error("Direct connection test failed")
    
    pool_result = asyncio.run(test_connection_pool())
    if pool_result:
        logger.info("Connection pool test completed successfully")
    else:
        logger.error("Connection pool test failed")
    
    # Exit with appropriate status code
    sys.exit(0 if result and pool_result else 1) 