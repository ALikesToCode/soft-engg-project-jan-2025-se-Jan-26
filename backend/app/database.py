from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from .config import settings
from urllib.parse import urlparse, parse_qs
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
import uuid
import os
import asyncio
from typing import AsyncGenerator
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
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    pool_recycle=1800,
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
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class for declarative models
Base = declarative_base()

# Dependency to get async DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            # Set timezone for this session
            await session.execute(text("SET timezone = 'UTC'"))
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Function to initialize the database (create tables, etc.)
async def init_db():
    """Initialize the database by creating tables if they don't exist."""
    async with engine.begin() as conn:
        # Create schema if it doesn't exist
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
        await conn.execute(text("SET search_path TO public"))
    
    # Check if tables exist before recreating
    tables_exist = False
    async with async_session() as session:
        # Get a list of existing tables using SQLAlchemy select
        query = select(text("pg_catalog.pg_class.relname")) \
            .select_from(text("pg_catalog.pg_class JOIN pg_catalog.pg_namespace ON pg_catalog.pg_namespace.oid = pg_catalog.pg_class.relnamespace")) \
            .where(text("pg_catalog.pg_class.relkind = ANY (ARRAY['r'::VARCHAR, 'p'::VARCHAR])")) \
            .where(text("pg_catalog.pg_class.relpersistence != 't'::CHAR")) \
            .where(text("pg_catalog.pg_table_is_visible(pg_catalog.pg_class.oid)")) \
            .where(text("pg_catalog.pg_namespace.nspname != 'pg_catalog'::VARCHAR"))
            
        result = await session.execute(query)
        existing_tables = [row[0] for row in result.fetchall()]
        logger.debug(f"Existing tables: {existing_tables}")
        
        # Check if core tables exist (using 'users' as a marker)
        if 'users' in existing_tables:
            tables_exist = True
    
    # Only create tables if they don't exist
    if not tables_exist:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            # Create the course status enum type if it doesn't exist
            await conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'coursestatus') THEN
                        CREATE TYPE coursestatus AS ENUM ('DRAFT', 'ACTIVE', 'ARCHIVED');
                    END IF;
                END $$;
            """))
                        
            # Create all tables defined in the models
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created successfully")
    else:
        logger.info("Database tables already exist, skipping creation")

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
