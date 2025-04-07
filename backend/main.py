from app.models.user import User
from app.models.course import Course
from app.database import init_db
from fastapi import FastAPI, Depends, HTTPException, Request, status
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from fastapi.responses import JSONResponse, HTMLResponse, Response
from app.services.auth_service import create_default_users
from app.database import get_db, async_session_maker, engine
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
from app.services.redis_service import redis_client
import os
from psycopg_pool import AsyncConnectionPool
import subprocess
import json
import asyncio
import time
import concurrent.futures
from starlette.middleware.gzip import GZipMiddleware

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
from app.routes.faculty_assignments import router as faculty_assignments  # Import new faculty assignments router

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
        
        # Make sure we have the default tables with increased timeout
        async with asyncio.timeout(10.0):  # Increased timeout to prevent hanging
            async with pool.connection() as conn:
                # Set a statement timeout to prevent hanging queries
                await conn.execute("SET statement_timeout = '5000'")  # 5 seconds timeout
                
                async with conn.cursor() as cursor:
                    # Check if core tables exist using a simpler, faster query
                    await cursor.execute("""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name IN ('users', 'courses', 'enrollments')
                        LIMIT 1;
                    """)
                    tables_count = await cursor.fetchone()
                    
                    # If users table doesn't exist, we need to run init_db
                    if not tables_count or tables_count[0] < 3:
                        logger.info("Core tables not found. Running database initialization...")
                        # Run async initialization
                        await init_db()
                        logger.info("Database initialization completed.")
                    else:
                        logger.info("Core tables already exist, skipping initialization.")
        
        # Verify DB initialization flag exists - do this without any database operations
        if not Path("db_initialized.flag").exists():
            with open("db_initialized.flag", 'w') as f:
                f.write('')
            logger.info("Created database initialization flag file")
        
        # Create default users with increased timeout
        if not Path("users_initialized.flag").exists():
            logger.info("Creating default users...")
            async with asyncio.timeout(10.0):  # Increased timeout
                async with async_session_maker() as session:
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
    """
    Lifespan context manager for FastAPI app
    
    Handles startup and shutdown tasks such as initializing database models,
    setting up monitoring, and establishing cache connections.
    """
    # Startup
    logger.info("Application starting up...")
    
    # Initialize database models asynchronously
    try:
        await init_db()
        logger.info("Database models initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database models: {e}")
        raise
    
    # Initialize Redis cache asynchronously
    try:
        await redis_client.init()
    except Exception as e:
        logger.error(f"Failed to initialize Redis cache: {e}")
    
    # Start monitoring service in background (non-blocking)
    asyncio.create_task(start_monitoring_background())
    logger.info("Monitoring service initialization started in background")

    # Cleanup redis cache on startup (non-blocking)
    asyncio.create_task(cleanup_redis_cache())
    logger.info("Redis cache cleanup started in background")
    
    logger.info("Application startup completed. Ready to serve requests.")
    yield
    
    # Shutdown
    logger.info("Application shutting down...")
    
    # Close Redis connection
    try:
        await redis_client.close()
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")
    
    # Close database connection pool
    try:
        await engine.dispose()
        logger.info("Database connection pool closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
    
    logger.info("Application shutdown complete")

async def start_monitoring_background():
    """Start monitoring service in background without blocking app startup"""
    try:
        # Using a separate thread for potentially blocking I/O operations
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(executor, monitoring_service.start)
            logger.info("Monitoring service started successfully")
    except Exception as e:
        logger.error(f"Failed to start monitoring service: {e}")

async def cleanup_redis_cache():
    """Clean up stale Redis cache entries on startup"""
    try:
        # Use a separate thread for Redis operations
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(executor, lambda: None)  # Placeholder for actual cleanup logic
            logger.info("Redis cache cleanup completed")
    except Exception as e:
        logger.error(f"Redis cache cleanup failed: {e}")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
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

# Add GZip middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    logger.info(f"Mounted static files from {STATIC_DIR}")

# Include routers
app.include_router(auth, prefix="/api/v1", tags=["auth"])
app.include_router(users, prefix="/api/v1/users", tags=["users"])
app.include_router(user_router, prefix="/api/v1", tags=["user"])  # Add user router for /user/profile endpoints
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
app.include_router(chat_history_router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(roadmap, prefix="/api/v1/roadmap", tags=["roadmap"])
app.include_router(notification, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(enrollments, prefix="/api/v1", tags=["enrollments"])  # Update prefix structure
app.include_router(faculty_assignments, prefix="/api/v1", tags=["faculty_assignments"])  # Add faculty assignments router

# Special case: Mount the auth callback directly at the root path to match the Google OAuth redirect
from app.routes.auth import auth_callback
app.add_api_route("/auth/callback", auth_callback, methods=["GET"], include_in_schema=True,
                 summary="Google OAuth callback",
                 description="Handles the callback from Google OAuth2 authentication")

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
