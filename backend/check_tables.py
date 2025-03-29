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

async def check_tables():
    """Check if LangGraph checkpoint tables and vector store collections exist"""
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
        
        # Get all tables in the database
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = await cur.fetchall()
            
            logger.info(f"Found {len(tables)} tables in the database:")
            for table in tables:
                logger.info(f"- {table[0]}")
            
            # Check for LangGraph checkpoint tables
            langgraph_tables = ['checkpoints', 'checkpoint_blobs', 'checkpoint_writes', 'checkpoint_migrations']
            logger.info("\nChecking LangGraph checkpoint tables:")
            for table_name in langgraph_tables:
                await cur.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = '{table_name}'
                    );
                """)
                exists = await cur.fetchone()
                if exists[0]:
                    # Count rows
                    await cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = await cur.fetchone()
                    logger.info(f"- {table_name}: EXISTS with {count[0]} rows")
                else:
                    logger.info(f"- {table_name}: MISSING")
            
            # Check for vector store collections
            vector_tables = ['langchain_pg_collection', 'langchain_pg_embedding']
            logger.info("\nChecking vector store tables:")
            for table_name in vector_tables:
                await cur.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = '{table_name}'
                    );
                """)
                exists = await cur.fetchone()
                if exists[0]:
                    # Count rows
                    await cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = await cur.fetchone()
                    logger.info(f"- {table_name}: EXISTS with {count[0]} rows")
                    
                    # If it's the collection table, show collections
                    if table_name == 'langchain_pg_collection' and count[0] > 0:
                        await cur.execute("SELECT name FROM langchain_pg_collection")
                        collections = await cur.fetchall()
                        logger.info("  Collections:")
                        for collection in collections:
                            logger.info(f"  - {collection[0]}")
                else:
                    logger.info(f"- {table_name}: MISSING")
            
            # Check for pgvector extension
            await cur.execute("""
                SELECT EXISTS(
                    SELECT FROM pg_extension WHERE extname = 'vector'
                );
            """)
            vector_ext = await cur.fetchone()
            if vector_ext[0]:
                logger.info("\npgvector extension is installed.")
            else:
                logger.info("\npgvector extension is NOT installed.")
        
        # Close the connection
        await conn.close()
        logger.info("\nDatabase connection closed.")
        return True
    except Exception as e:
        logger.error(f"Error checking tables: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Checking database tables...")
    asyncio.run(check_tables()) 