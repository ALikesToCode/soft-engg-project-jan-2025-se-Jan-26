from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from .config import settings
from urllib.parse import urlparse, parse_qs
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
import uuid

# Parse the database URL to handle SSL properly
url = urlparse(settings.DATABASE_URL)
query_params = parse_qs(url.query)

# Remove sslmode from the URL and handle it in connect_args
ssl_mode = query_params.pop('sslmode', ['prefer'])[0]
cleaned_url = f"{url.scheme}://{url.netloc}{url.path}"
if query_params:
    cleaned_url += '?' + '&'.join(f"{k}={v[0]}" for k, v in query_params.items())

# Create async engine with proper SSL configuration
engine = create_async_engine(
    cleaned_url.replace("postgres://", "postgresql+asyncpg://"),
    future=True,
    echo=True,
    poolclass=NullPool,
    connect_args={
        "ssl": ssl_mode == "require"
    }
)


# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class for declarative models
Base = declarative_base()

# Dependency to get async DB session
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Initialize the database tables
async def init_db():
    """
    Initialize the database tables.
    
    This function creates all tables defined in the models if they don't already exist.
    It should be called during application startup to ensure the database schema is properly set up.
    
    Returns:
        None
    """
    # Import models here to ensure they are registered with Base
    # but avoid circular imports
    from app.models.user import User
    from app.models.course import Course, CourseEnrollment
    from app.models.assignment import Assignment, Submission
    from app.models.role import Role
    from datetime import datetime
    from sqlalchemy import inspect
    
    # Check if tables already exist
    async with engine.begin() as conn:
        # Use run_sync to properly handle inspection on async connection
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        
        # Only create tables if they don't exist
        if 'users' not in tables:
            print("Creating database tables for the first time...")
            await conn.run_sync(Base.metadata.create_all)
            
            # Create default users only if tables were just created
            async with async_session() as session:
                try:
                    # Create default faculty user
                    faculty_user = User(
                        id=uuid.UUID('123e4567-e89b-12d3-a456-426614174000'),
                        email="faculty@study.iitm.ac.in",
                        name="Default Faculty",
                        role="faculty",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(faculty_user)
                    
                    # Create default support user
                    support_user = User(
                        id=uuid.UUID('123e4567-e89b-12d3-a456-426614174001'),
                        email="support@study.iitm.ac.in",
                        name="Support Team",
                        role="support",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(support_user)
                    
                    await session.commit()
                    print("Default users created successfully.")
                except Exception as e:
                    await session.rollback()
                    print(f"Error creating default users: {e}")
        else:
            print("Database tables already exist, skipping initialization.")

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
