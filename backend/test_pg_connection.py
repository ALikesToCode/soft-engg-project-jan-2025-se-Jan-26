"""
Test PostgreSQL connection and pgvector extension
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    logger.error("DATABASE_URL environment variable is not set")
    sys.exit(1)

logger.info(f"Using DATABASE_URL: {database_url}")

# Convert SQLAlchemy URL format to psycopg format
psycopg_connection_string = database_url
if "postgresql+asyncpg://" in psycopg_connection_string:
    psycopg_connection_string = psycopg_connection_string.replace("postgresql+asyncpg://", "postgresql://")
    logger.info(f"Converted connection string for psycopg: {psycopg_connection_string}")

# Test connection with psycopg
try:
    import psycopg
    logger.info("Connecting to PostgreSQL...")
    
    with psycopg.connect(psycopg_connection_string) as conn:
        with conn.cursor() as cur:
            # Get PostgreSQL version
            cur.execute("SELECT version()")
            version = cur.fetchone()
            logger.info(f"PostgreSQL Version: {version[0]}")
            
            # Check for pgvector extension
            cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'")
            pgvector = cur.fetchone()
            if pgvector:
                logger.info(f"pgvector extension is installed (version: {pgvector[1]})")
            else:
                logger.warning("pgvector extension is NOT installed")
                
                # Try to install it
                try:
                    logger.info("Attempting to install pgvector extension...")
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                    conn.commit()
                    logger.info("pgvector extension installed successfully")
                except Exception as e:
                    logger.error(f"Failed to install pgvector extension: {e}")
                    
            # Test if we can create a vector column (if pgvector is installed)
            try:
                cur.execute("CREATE TEMP TABLE vector_test (id SERIAL PRIMARY KEY, embedding VECTOR(3))")
                cur.execute("INSERT INTO vector_test (embedding) VALUES ('[1, 2, 3]')")
                cur.execute("SELECT * FROM vector_test")
                result = cur.fetchone()
                logger.info(f"Vector test successful: {result}")
            except Exception as e:
                logger.error(f"Vector test failed: {e}")
    
    logger.info("Database connection test completed successfully")
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    sys.exit(1) 