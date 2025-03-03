from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from .config import settings
from urllib.parse import urlparse, parse_qs

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
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
