import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.config import settings

async def test_db_connection():
    # Open a file for writing
    with open("db_test_output.txt", "w") as f:
        # Print the database URL
        f.write(f"Database URL: {settings.DATABASE_URL}\n")
        
        # Create engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True,
            poolclass=NullPool
        )
        
        # Create session
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Test connection
        try:
            async with engine.begin() as conn:
                # Check if connection works
                result = await conn.execute("SELECT 1")
                f.write(f"Connection successful: {result.scalar()}\n")
                
                # Get list of tables
                tables = await conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                f.write("Tables in database:\n")
                for table in tables:
                    f.write(f"  - {table[0]}\n")
        except Exception as e:
            f.write(f"Error connecting to database: {e}\n")
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_db_connection()) 