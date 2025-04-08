from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from .config import settings
from urllib.parse import urlparse, parse_qs
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
import uuid
import os
import asyncio
from typing import AsyncGenerator, Any
from fastapi import Depends
from datetime import datetime, UTC
import re
from sqlalchemy import inspect, text, select
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Parse the database URL to handle SSL properly
url = urlparse(settings.DATABASE_URL)
query_params = parse_qs(url.query)

# Extract schema from path if present
path_parts = url.path.split('/')
db_name = path_parts[-1]
schema_name = 'public'  # Default schema

# Handle SSL mode properly
ssl_mode = query_params.pop('sslmode', ['prefer'])[0] if 'sslmode' in query_params else None
    
# If sslmode is not in query params but in the URL string (malformed URL)
if ssl_mode is None:
    if "?sslmode" in settings.DATABASE_URL:
        # Fix common issue with malformed sslmode parameter
        if "?sslmode=require" in settings.DATABASE_URL:
            ssl_mode = 'require'
        else:
            fixed_url = settings.DATABASE_URL.replace("?sslmode", "?sslmode=require")
            logger.warning(f"Fixed malformed URL: {fixed_url}")
            url = urlparse(fixed_url)
            query_params = parse_qs(url.query)
            ssl_mode = 'require'
    else:
        ssl_mode = 'prefer'  # Default if not specified

# Create a clean URL without sslmode for SQLAlchemy
cleaned_url = f"{url.scheme}://{url.netloc}{url.path}"
if query_params:
    cleaned_url += '?' + '&'.join(f"{k}={v[0]}" for k, v in query_params.items())

logger.info(f"Using database connection with SSL mode: {ssl_mode}")

# Create async engine with proper SSL configuration and optimized connection settings
engine = create_async_engine(
    cleaned_url.replace("postgres://", "postgresql+asyncpg://"),
    future=True,
    echo=settings.DEBUG,  # Only echo in debug mode
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=30,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    connect_args={
        "ssl": ssl_mode == "require",
        "server_settings": {
            "search_path": schema_name,
            "application_name": "SE Team 26 API",
            "statement_timeout": "5000",
            "idle_in_transaction_session_timeout": "120000"
        }
    }
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Create base class for declarative models
Base = declarative_base()

# Dependency to get async DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get a database session
    
    Yields:
        AsyncSession: SQLAlchemy async session
    """
    async with async_session_maker() as session:
        try:
            # Set timezone for this session
            await session.execute(text("SET timezone = 'UTC'"))
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()

# Function to initialize the database (create tables, etc.)
async def init_db():
    """
    Initialize database models by creating all tables
    
    This function creates all tables defined as SQLAlchemy models
    that inherit from the Base class.
    """
    async with engine.begin() as conn:
        # Check if tables already exist
        # Create a function that will run in sync context to inspect the connection
        async def get_table_names():
            def _get_tables(sync_conn):
                sync_inspector = inspect(sync_conn)
                return sync_inspector.get_table_names()
            
            return await conn.run_sync(_get_tables)
        
        tables = await get_table_names()
        
        if not tables:
            logger.info("No existing tables found, creating all database tables")
            
            # Create tables in proper dependency order
            def create_tables_in_order(sync_conn):
                # Get metadata
                metadata = Base.metadata
                
                # Create tables in dependency order
                metadata.create_all(sync_conn, checkfirst=True)
            
            await conn.run_sync(create_tables_in_order)
            logger.info("All database tables created successfully")
        else:
            logger.info(f"Found existing tables: {tables}")
            # Create only missing tables
            existing_tables = set(tables)
            model_tables = set(Base.metadata.tables.keys())
            missing_tables = model_tables - existing_tables
            
            if missing_tables:
                logger.info(f"Creating missing tables: {missing_tables}")
                # Create all missing tables at once respecting dependencies
                def create_missing_tables(sync_conn):
                    metadata = Base.metadata
                    
                    # Sort missing tables based on dependencies
                    sorted_tables = []
                    for table_name in missing_tables:
                        if table_name in metadata.tables:
                            sorted_tables.append(metadata.tables[table_name])
                    
                    # Create tables in correct dependency order
                    # This will handle the proper creation order automatically
                    metadata.create_all(sync_conn, tables=sorted_tables, checkfirst=True)
                
                await conn.run_sync(create_missing_tables)
                logger.info("Missing tables created successfully")
            else:
                logger.info("All tables already exist, skipping table creation")

# Custom UUID type for SQLite compatibility
class UUID(TypeDecorator):
    """Platform-independent UUID type.
    
    Uses PostgreSQL's UUID type when available, otherwise uses CHAR(36).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value

# Run database initialization
if __name__ == "__main__":
    asyncio.run(init_db())

async def verify_db_connection():
    """
    Verify database connection is working
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.scalar()
            return row == 1
    except Exception as e:
        logger.error(f"Database connection verification failed: {str(e)}")
        return False

async def get_db_health():
    """
    Get database health information
    
    Returns:
        dict: Database health information including connection status,
              pool statistics, and version information
    """
    try:
        # Check connection
        is_connected = await verify_db_connection()
        
        # Get database version
        version_info = None
        if is_connected:
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT version()"))
                version_info = result.scalar()
        
        # Get pool statistics
        pool_status = {
            "size": engine.pool.size(),
            "checkedin": engine.pool.checkedin(),
            "checkedout": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
        }
        
        return {
            "connected": is_connected,
            "version": version_info,
            "pool": pool_status,
            "url": str(engine.url).replace(engine.url.password or "", "********") if engine.url.password else str(engine.url),
        }
    except Exception as e:
        logger.error(f"Failed to get database health: {str(e)}")
        return {
            "connected": False,
            "error": str(e)
        }
