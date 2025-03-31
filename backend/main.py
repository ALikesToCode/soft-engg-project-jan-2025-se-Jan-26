from app.models.user import User
from app.models.course import Course
from app.database import init_db
from fastapi import FastAPI, Depends, HTTPException, Request, status
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from fastapi.responses import JSONResponse, HTMLResponse, Response
from app.services.auth_service import create_default_users
from app.database import get_db, async_session
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_service import oauth2_scheme
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.routes.auth import router as auth_router
from app.routes.user import router as user_router
from app.routes.user_routes import router as user_routers
from app.routes.llm import router as chat
from app.routes.chat import router as chat_history_router
from app.routes.assignment import router as assignment_router
from app.routes.faq import router as faq_router
from app.routes.system_settings import router as system_settings_router
from app.routes.course_routes import course_router
from app.routes.academic_integrity import router as academic_integrity_router
from app.services.api_functions import *  # Import all API function declarations
from app.routes import monitoring
from app.services.monitoring_service import monitoring_service
from app.services.cache_service import start_cleanup_task
import logging
from app.utils.logging_config import configure_logging
from app.middleware import LoggingMiddleware
from contextlib import asynccontextmanager
from app.routes.notification import router as notification
import os
from psycopg_pool import AsyncConnectionPool
import subprocess
import json
import asyncio

# Import the modules individually instead of from app.routes
from app.routes.auth import router as auth
from app.routes.user import router as users  # Change this to use the existing user_router
from app.routes.healthcheck import router as healthcheck  
from app.routes.courses import router as courses
from app.routes.module import router as module
from app.routes.assignment import router as assignments
from app.routes.faq import router as faqs
from app.routes.lectures import router as lectures
from app.routes.academic_integrity import router as academic_integrity
from app.routes.vector_search import router as vector_search
from app.routes.upload import router as upload
from app.routes.llm import router as llm
from app.routes.roadmap import router as roadmap
from app.routes.enrollments import router as enrollments  # Import new enrollments router

# Apply Pydantic v1 patch for Python 3.13 compatibility
from app.utils.pydantic_patch import apply_patch
apply_patch()

# Apply passlib bcrypt patch for newer bcrypt versions
from app.utils.passlib_patch import apply_patch as apply_passlib_patch
apply_passlib_patch()

# Configure logging
logger = configure_logging()
logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

# Get the absolute path to the static directory
STATIC_DIR = Path(__file__).parent / "static"

# Function to verify and create required database schemas
async def verify_and_create_schemas(pool):
    logger.info("Verifying database schemas...")
    
    try:
        # Skip langchain-related schema verification since we're not using it anymore
        logger.info("Skipping LangChain schema verification")
        
        # Make sure we have the default tables with timeout
        async with asyncio.timeout(5.0):  # Add timeout to prevent hanging
            async with pool.connection() as conn:
                async with conn.cursor() as cursor:
                    # Check if core tables exist
                    await cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'users'
                        );
                    """)
                    users_table_exists = await cursor.fetchone()
                    
                    # If users table doesn't exist, we need to run init_db
                    if not users_table_exists or not users_table_exists[0]:
                        logger.info("Core tables not found. Running database initialization...")
                        # Run async initialization
                        await init_db()
                        logger.info("Database initialization completed.")
                    else:
                        logger.info("Core tables already exist, skipping initialization.")
        
        # Verify DB initialization flag exists
        if not Path("db_initialized.flag").exists():
            with open("db_initialized.flag", 'w') as f:
                f.write('')
            logger.info("Created database initialization flag file")
        
        # Create default users
        if not Path("users_initialized.flag").exists():
            logger.info("Creating default users...")
            async with asyncio.timeout(5.0):  # Add timeout
                async with async_session() as session:
                    await create_default_users(session)
            with open("users_initialized.flag", 'w') as f:
                f.write('')
            logger.info("Default users created and flag file updated.")
        else:
            logger.info("Default users already created, skipping.")
            
    except asyncio.TimeoutError:
        logger.error("Timeout verifying database schemas, but continuing startup")
    except Exception as e:
        logger.error(f"Error verifying database schemas: {str(e)}")
        # Don't raise - allow startup to continue with limited functionality
        logger.warning("Continuing with application startup despite schema verification issues")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for application startup and shutdown"""
    # Initialize database on startup
    logger.info("Initializing database...")
    # Check if we've already run a full initialization before
    db_initialized_flag = Path("db_initialized.flag")
    if not db_initialized_flag.exists():
        logger.info("First time initialization - creating all database objects")
        try:
            # Add timeout for database initialization
            async with asyncio.timeout(10.0):
                await init_db()
            # Create the flag file to indicate we've completed a full initialization
            db_initialized_flag.touch()
            logger.info("Database initialization completed and flag file created")
        except asyncio.TimeoutError:
            logger.warning("Database initialization timed out, continuing with limited functionality")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)} - continuing with limited functionality")
    else:
        logger.info("Database previously initialized, skipping full initialization")
    
    # Create default users
    logger.info("Creating default users...")
    # Only create default users if we're doing the first initialization 
    # or if users_initialized.flag doesn't exist
    users_initialized_flag = Path("users_initialized.flag")
    if not db_initialized_flag.exists() or not users_initialized_flag.exists():
        try:
            async with asyncio.timeout(5.0):  # Add timeout
                async with async_session() as session:
                    await create_default_users(session)
                # Create flag to indicate users have been set up
                users_initialized_flag.touch()
        except asyncio.TimeoutError:
            logger.warning("Default user creation timed out, continuing startup")
        except Exception as e:
            logger.error(f"Error creating default users: {e}")
    else:
        logger.info("Default users already initialized, skipping")
    
    # Start monitoring service background tasks with timeout
    logger.info("Starting monitoring service...")
    monitoring_started = False
    try:
        # Add a timeout to prevent hanging on monitoring startup
        monitoring_task = asyncio.create_task(monitoring_service.start_background_tasks())
        await asyncio.wait_for(monitoring_task, timeout=3.0)
        monitoring_started = True
        logger.info("Monitoring service started successfully")
    except asyncio.TimeoutError:
        logger.warning("Monitoring service startup timed out - continuing anyway")
    except Exception as e:
        logger.error(f"Error starting monitoring service: {str(e)} - continuing anyway")

    # Set up database connection
    logger.info("Setting up database connection...")
    connection_string = os.getenv("DATABASE_URL")
    
    # Simplified connection string check and preparation
    if connection_string:
        if "sslmode=require" not in connection_string:
            if "?" in connection_string:
                connection_string = connection_string + "&sslmode=require"
            else:
                connection_string = connection_string + "?sslmode=require"
                
        # Convert SQLAlchemy URL format to psycopg format
        psycopg_connection_string = connection_string.replace("postgresql+asyncpg://", "postgresql://")
        
        logger.info(f"Using psycopg connection string format: {psycopg_connection_string}")
        
        # Create connection pool with reduced values for faster startup
        connection_kwargs = {
            "min_size": 1,      # Reduced from 2
            "max_size": 5,      # Reduced from 10
            "max_idle": 60.0,   # Reduced from 300
            "timeout": 10.0     # Reduced from 30
        }
        
        try:
            # Create the connection pool with psycopg
            logger.info("Creating psycopg connection pool...")
            pool = AsyncConnectionPool(psycopg_connection_string, **connection_kwargs)
            
            # Open the pool with proper async handling and timeout
            try:
                await asyncio.wait_for(pool.open(wait=True), timeout=10.0)
                logger.info("Successfully connected to database pool")
                
                # Store the pool in the app state
                app.state.pool = pool
                
                # Set autocommit on connections
                async def setup_connection(conn):
                    await conn.set_autocommit(True)
                pool.configure_connection = setup_connection
                
                # Verify and create schemas with a timeout
                await verify_and_create_schemas(pool)
            except asyncio.TimeoutError:
                logger.error("Timeout opening database pool - continuing with limited functionality")
            
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            logger.error("Failed to create connection pool or initialize schemas")
            # Don't raise the exception, allow the application to start with limited functionality
    else:
        logger.error("DATABASE_URL not set, starting with limited functionality")
    
    # Start cleanup task for redis cache with timeout
    try:
        # Add a timeout to prevent hanging on cache startup
        cleanup_task = asyncio.create_task(start_cleanup_task())
        # Wait for the task to complete with a reduced timeout
        await asyncio.wait_for(cleanup_task, timeout=3.0)
        logger.info("Redis cache cleanup task started")
    except asyncio.TimeoutError:
        logger.warning("Redis cache cleanup task startup timed out - continuing anyway")
    except Exception as e:
        logger.warning(f"Failed to start Redis cache cleanup task: {str(e)} - continuing anyway")
    
    logger.info("Application startup completed - ready to serve requests")
    
    # Application is now ready - yield control back to FastAPI
    yield
    
    # Shutdown tasks
    logger.info("Shutting down application...")
    
    # Close the connection pool
    if hasattr(app.state, "pool"):
        logger.info("Closing database connection pool...")
        try:
            await asyncio.wait_for(app.state.pool.close(), timeout=5.0)
            logger.info("Database connection pool closed")
        except asyncio.TimeoutError:
            logger.warning("Timeout closing database pool - forcing shutdown")
        except Exception as e:
            logger.error(f"Error closing database pool: {str(e)}")
        
    # Stop monitoring service only if it was started
    if monitoring_started:
        logger.info("Stopping monitoring service...")
        try:
            await asyncio.wait_for(monitoring_service.stop_background_tasks(), timeout=3.0)
        except asyncio.TimeoutError:
            logger.warning("Timeout stopping monitoring service - forcing shutdown")
        except Exception as e:
            logger.error(f"Error stopping monitoring service: {str(e)}")
    
    logger.info("Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    logger.info(f"Mounted static files from {STATIC_DIR}")

# Include routers
app.include_router(auth, prefix="/api/v1", tags=["auth"])
app.include_router(users, prefix="/api/v1/users", tags=["users"])
app.include_router(healthcheck, prefix="/api/v1", tags=["system"])
app.include_router(courses,prefix="/api/v1", tags=["courses"])
app.include_router(course_router,prefix="/api/v1", tags=["faculty-courses"])
app.include_router(module, prefix="/api/v1/modules", tags=["modules"])
app.include_router(assignments, prefix="/api/v1/assignments", tags=["assignments"])
app.include_router(academic_integrity, prefix="/api/v1/academic-integrity", tags=["academic-integrity"])
app.include_router(faqs, prefix="/api/v1/faqs", tags=["faqs"])
app.include_router(lectures, prefix="/api/v1/lectures", tags=["lectures"])
app.include_router(vector_search, prefix="/api/v1/vector", tags=["search"])
app.include_router(upload, prefix="/api/v1/upload", tags=["files"])
app.include_router(llm, prefix="/api/v1/llm", tags=["llm"])
app.include_router(roadmap, prefix="/api/v1/roadmap", tags=["roadmap"])
app.include_router(notification, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(enrollments, prefix="/api/v1", tags=["enrollments"])  # Update prefix structure

# Monitoring endpoints
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])

# Root endpoint - optimized for faster response
@app.get("/", include_in_schema=False)
async def root():
    # Simplified response for faster performance
    return JSONResponse(content={"status": "ok", "version": settings.APP_VERSION})

# Health check for API root - optimized
@app.get("/health", include_in_schema=False)
async def health_check():
    # Simple response that avoids any database calls
    return JSONResponse(status_code=200, content={"status": "ok"})

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENV == "development"
    )
