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
from app.routes.llm import router as chat, checkpointer
from app.routes.assignment import router as assignment_router
from app.routes.faq import router as faq_router
from app.routes.system_settings import router as system_settings_router
from app.routes.courses import router as courses_router
from app.routes.course_routes import course_router
from app.routes.academic_integrity import router as academic_integrity_router
from app.services.api_functions import *  # Import all API function declarations
from app.routes import monitoring
from app.services.monitoring_service import monitoring_service
import logging
from app.utils.logging_config import configure_logging
from app.middleware import LoggingMiddleware
from contextlib import asynccontextmanager
from app.routes.notification import router as notification
import os
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import START, MessagesState, StateGraph
from app.routes.llm import call_llm
import subprocess
import json

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
    required_tables = {
        # LangGraph tables
        "checkpoints": """
            CREATE TABLE IF NOT EXISTS checkpoints (
                id SERIAL PRIMARY KEY,
                thread_id TEXT NOT NULL,
                state JSONB NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """,
        "checkpoint_blobs": """
            CREATE TABLE IF NOT EXISTS checkpoint_blobs (
                id SERIAL PRIMARY KEY,
                thread_id TEXT NOT NULL,
                blob_id TEXT NOT NULL,
                blob BYTEA NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(thread_id, blob_id)
            )
        """,
        "checkpoint_writes": """
            CREATE TABLE IF NOT EXISTS checkpoint_writes (
                id SERIAL PRIMARY KEY,
                thread_id TEXT NOT NULL,
                write_id TEXT NOT NULL,
                write JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(thread_id, write_id)
            )
        """,
        "checkpoint_migrations": """
            CREATE TABLE IF NOT EXISTS checkpoint_migrations (
                id SERIAL PRIMARY KEY,
                version INTEGER NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """,
        # Vector store tables
        "langchain_pg_collection": """
            CREATE TABLE IF NOT EXISTS langchain_pg_collection (
                name VARCHAR(50) PRIMARY KEY,
                cmetadata JSONB
            )
        """,
        "langchain_pg_embedding": """
            CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
                uuid UUID PRIMARY KEY,
                collection_name VARCHAR(50) NOT NULL,
                embedding vector(1536),
                document TEXT,
                cmetadata JSONB,
                custom_id TEXT,
                CONSTRAINT fk_collection
                    FOREIGN KEY (collection_name) 
                    REFERENCES langchain_pg_collection (name) 
                    ON DELETE CASCADE
            )
        """,
        "vector_store": """
            -- This is just to check if the vector_store collection exists
            -- Will create if it doesn't exist
            INSERT INTO langchain_pg_collection (name, cmetadata)
            VALUES ('vector_store', '{}')
            ON CONFLICT (name) DO NOTHING
        """
    }
    
    # Create schema if it doesn't exist
    async with pool.connection() as conn:
        await conn.execute("CREATE SCHEMA IF NOT EXISTS public")
        
        # Check which tables exist
        result = await conn.execute("""
            SELECT tablename FROM pg_catalog.pg_tables 
            WHERE schemaname = 'public'
        """)
        existing_tables = [row[0] for row in await result.fetchall()]
        logger.info(f"Existing tables: {existing_tables}")
        
        # Create missing tables
        for table_name, create_sql in required_tables.items():
            if table_name not in existing_tables:
                logger.info(f"Creating table: {table_name}")
                await conn.execute(create_sql)
            else:
                logger.info(f"Table already exists: {table_name}")
        
        # Check if pgvector extension is available
        try:
            result = await conn.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
            if await result.fetchone() is None:
                logger.info("pgvector extension not found, attempting to create it")
                try:
                    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                    logger.info("Successfully created pgvector extension")
                except Exception as e:
                    logger.warning(f"Could not create pgvector extension: {str(e)}")
            else:
                logger.info("pgvector extension already exists")
        except Exception as e:
            logger.warning(f"Error checking pgvector extension: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for application startup and shutdown"""
    try:
        # Initialize database on startup
        logger.info("Initializing database...")
        # Check if we've already run a full initialization before
        db_initialized_flag = Path("db_initialized.flag")
        if not db_initialized_flag.exists():
            logger.info("First time initialization - creating all database objects")
            await init_db()
            # Create the flag file to indicate we've completed a full initialization
            db_initialized_flag.touch()
            logger.info("Database initialization completed and flag file created")
        else:
            logger.info("Database previously initialized, skipping full initialization")
        
        # Create default users
        logger.info("Creating default users...")
        # Only create default users if we're doing the first initialization 
        # or if users_initialized.flag doesn't exist
        users_initialized_flag = Path("users_initialized.flag")
        if not db_initialized_flag.exists() or not users_initialized_flag.exists():
            async with async_session() as session:
                try:
                    await create_default_users(session)
                    # Create flag to indicate users have been set up
                    users_initialized_flag.touch()
                except Exception as e:
                    logger.error(f"Error creating default users: {e}")
        else:
            logger.info("Default users already initialized, skipping")
        
        # Start monitoring service background tasks
        logger.info("Starting monitoring service...")
        await monitoring_service.start_background_tasks()

        # Set up LangGraph with Postgres
        logger.info("Setting up LangGraph with Postgres...")
        connection_string = os.getenv("DATABASE_URL")
        # Verify the connection string is properly formatted
        if not connection_string or not connection_string.endswith("require"):
            logger.error(f"Invalid DATABASE_URL format: {connection_string}")
            if connection_string and "?sslmode" in connection_string:
                # Fix common issue with sslmode parameter
                connection_string = connection_string.replace("?sslmode", "?sslmode=require")
                logger.info(f"Fixed DATABASE_URL: {connection_string}")
            else:
                # Add sslmode=require if not present
                if "?" in connection_string:
                    connection_string = connection_string + "&sslmode=require"
                else:
                    connection_string = connection_string + "?sslmode=require"
                logger.info(f"Added sslmode=require to DATABASE_URL: {connection_string}")
                
        # Convert SQLAlchemy URL format to psycopg format
        # psycopg doesn't support the postgresql+asyncpg:// prefix or dialect options
        psycopg_connection_string = connection_string
        if "postgresql+asyncpg://" in psycopg_connection_string:
            psycopg_connection_string = psycopg_connection_string.replace("postgresql+asyncpg://", "postgresql://")
            
        # Force hostname connection method (disable socket connection attempts)
        if "ep-weathered-breeze-a8jcdehd-pooler.eastus2.azure.neon.tech" in psycopg_connection_string:
            # We're using a Neon DB connection - ensure host connection method
            if "?" in psycopg_connection_string:
                # Remove invalid host_type parameter if present
                if "&host_type=host" in psycopg_connection_string:
                    psycopg_connection_string = psycopg_connection_string.replace("&host_type=host", "")
            else:
                # No need to add invalid parameters
                pass
        
        logger.info(f"Using psycopg connection string format: {psycopg_connection_string}")
        
        # Configure more resilient connection parameters
        connection_kwargs = {
            "autocommit": True,
            # Add connection timeout settings
            "connect_timeout": 30,  # Increased from 10 to 30 seconds
            # Force SSL for Neon DB
            "sslmode": "require",
            # Remove invalid host_type parameter
            # Configure automatic retry behavior
            "application_name": "langraph_checkpointer",
            # Keep connections alive
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
        
        try:
            # Check psycopg version
            import psycopg
            logger.info(f"Using psycopg version: {psycopg.__version__}")
            
            # Create a connection pool with more resilient settings
            # Initialize directly with all parameters in constructor
            # Note: The warning about constructor deprecation is acceptable
            pool = AsyncConnectionPool(
                conninfo=psycopg_connection_string,
                kwargs=connection_kwargs, 
                min_size=1,
                max_size=5
            )
            
            # Verify connection works
            async with pool.connection() as conn:
                # Execute a simple query to verify connection
                result = await conn.execute("SELECT 1")
                logger.info("Database connection verified successfully")
                
            app.state.pool = pool
            
            # Verify and create required database schemas
            await verify_and_create_schemas(pool)
            
            # Initialize the checkpointer
            from app.routes.llm import checkpointer, llmapp
            saver = AsyncPostgresSaver(pool)
            await saver.setup()
            
            # Create the workflow
            workflow = StateGraph(state_schema=MessagesState)
            workflow.add_edge(START, "llm")
            workflow.add_node("llm", call_llm)
            
            # Set the global app and checkpointer objects
            app.state.checkpointer = saver
            app.state.llmapp = workflow.compile(checkpointer=saver)
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {str(e)}")
            logger.warning("LangGraph features will not be available")
        
        # Initialize vector store if needed (only once)
        vector_store_flag = Path("vector_store_initialized.flag")
        if not vector_store_flag.exists():
            logger.info("Vector store not initialized. Initializing...")
            try:
                # Run the vector store initialization script with retry mechanism
                max_retries = 3
                retry_count = 0
                success = False
                
                while retry_count < max_retries and not success:
                    logger.info(f"Attempting vector store initialization (attempt {retry_count + 1}/{max_retries})")
                    result = subprocess.run(
                        ["python", "initialize_vector_store.py"], 
                        capture_output=True, 
                        text=True
                    )
                    
                    if result.returncode == 0:
                        logger.info("Vector store initialized successfully.")
                        # Create flag file to indicate initialization complete
                        vector_store_flag.touch()
                        success = True
                    else:
                        logger.error(f"Vector store initialization attempt {retry_count + 1} failed: {result.stderr}")
                        # Check if this is a pgvector extension error
                        if "extension \"vector\" is not available" in result.stderr or "pgvector extension could not be installed" in result.stderr:
                            logger.warning("The PostgreSQL server may not have pgvector extension installed.")
                            logger.warning("Some AI features requiring vector search will be limited.")
                            # Create a flag file anyway to prevent repeated failures
                            Path("vector_store_unavailable.flag").touch()
                            logger.info("Created flag file to prevent repeated initialization attempts.")
                            break
                        
                        # If it's likely a connection issue, retry
                        if "connection" in result.stderr.lower() or "timeout" in result.stderr.lower():
                            retry_count += 1
                            if retry_count < max_retries:
                                # Exponential backoff
                                wait_time = 2 ** retry_count
                                logger.info(f"Waiting {wait_time} seconds before retrying...")
                                import asyncio
                                await asyncio.sleep(wait_time)
                        else:
                            # Non-connection error, no need to retry
                            break
                
                if not success and retry_count >= max_retries:
                    logger.error(f"Vector store initialization failed after {max_retries} attempts.")
            except Exception as e:
                logger.error(f"Error initializing vector store: {str(e)}")
        else:
            logger.info("Vector store already initialized, skipping initialization.")
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        
    yield
    
    try:
        # Stop monitoring service background tasks on shutdown
        logger.info("Stopping monitoring service...")
        await monitoring_service.stop_background_tasks()
        
        # Close pool connection
        if hasattr(app.state, "pool"):
            logger.info("Closing database connection pool...")
            try:
                await app.state.pool.close()
            except Exception as e:
                logger.error(f"Error closing pool: {e}")
                
        # Clean up other resources if needed
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}")

# Replace the FastAPI app instance with one that uses the lifespan handler
app = FastAPI(
    title="Support Dashboard API",
    description="""
# API for the support dashboard monitoring system

This API provides endpoints for managing the support dashboard, including user authentication, course management, and more.

## Features

- User authentication and management
- Course enrollment and management
- Assignment submission and grading
- AI-powered chat assistance
- System monitoring and health checks

## Running the Application

### Prerequisites
- Python 3.10+
- PostgreSQL database
- Redis server (for token management)

### Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/soft-engg-project-jan-2025-se-Jan-26.git
   cd soft-engg-project-jan-2025-se-Jan-26
   ```

2. Create and activate a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Create a `.env` file in the backend directory
   - Set required variables (see `.env.example` for reference)

### Running the Server
```bash
# From the backend directory
python -m uvicorn main:app --reload --port 8002 --host 0.0.0.0
```

The API will be available at:
- API Documentation: http://localhost:8002/docs
- ReDoc Documentation: http://localhost:8002/redoc
- API Endpoints: http://localhost:8002/api/v1/...

## Authentication

This API supports two authentication methods:

1. **JWT Bearer Token**: Obtain a token via `/api/v1/auth/login` endpoint
2. **Google OAuth2**: Use the Google login button in the Swagger UI or [login directly](/api/v1/auth/login/google)

### JWT Authentication

1. Use the `/api/v1/auth/login` endpoint with your email and password
2. Copy the returned access token
3. Click the "Authorize" button and enter the token in the format: `Bearer your_token`
4. Or use the "Auto-Authenticate" button after logging in to automatically apply your token

### Google OAuth Authentication

1. Click the "Authorize" button
2. Select "Google OAuth2" and click "Authorize"
3. Complete the Google authentication flow

### Default Test Accounts

- **Support User**:
  - Email: support@study.iitm.ac.in
  - Password: support123

- **Faculty User**:
  - Email: faculty@study.iitm.ac.in
  - Password: faculty123

- **Student User**:
  - Email: student@ds.study.iitm.ac.in
  - Password: student123
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_js_url="/static/swagger-ui-bundle.js",
    swagger_css_url="/static/swagger-ui.css",
    lifespan=lifespan
)

# Secret key for session middleware
if not settings.SESSION_SECRET:
    raise ValueError("SESSION_SECRET environment variable is not set")

# Configure CORS
if not settings.ALLOWED_ORIGINS:
    raise ValueError("ALLOWED_ORIGINS environment variable is not set")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Session Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)

# Add Logging Middleware
app.add_middleware(LoggingMiddleware)

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def root():
    return JSONResponse({
        "message": "Welcome to SE Team 26 API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "api_login": "/api-login",
        "openapi_json": "/openapi.json",
        "openapi_yaml": "/openapi.yaml",
        "download_yaml": "/openapi.yaml?download=true",
        "status": "operational",
        "environment": settings.ENV,
        "api_prefix": settings.API_PREFIX
    })

# Custom Swagger UI with OAuth2 support
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    swagger_ui_html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.APP_NAME} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        init_oauth={
            "clientId": settings.GOOGLE_CLIENT_ID,
            "clientSecret": settings.GOOGLE_CLIENT_SECRET,
            "appName": settings.APP_NAME,
            "usePkceWithAuthorizationCodeGrant": True,
            "scopes": ["openid", "email", "profile"],
            "useBasicAuthenticationWithAccessCodeGrant": True
        }
    )
    
    # Convert to string and add our custom button
    content = swagger_ui_html.body.decode("utf-8")
    
    # Add CSS for download button and auth helper
    custom_css = """
    <style>
        .download-yaml-btn {
            position: fixed;
            top: 70px;
            right: 20px;
            background-color: #4CAF50;
            color: white !important;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            z-index: 1000;
            font-size: 14px;
            font-family: sans-serif;
        }
        .download-yaml-btn:hover {
            background-color: #45a049;
        }
        
        .login-btn {
            position: fixed;
            top: 120px;
            right: 20px;
            background-color: #9C27B0;
            color: white !important;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            z-index: 1000;
            font-size: 14px;
            font-family: sans-serif;
        }
        .login-btn:hover {
            background-color: #7B1FA2;
        }
        
        .auth-status {
            position: fixed;
            top: 220px;
            right: 20px;
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            color: #333;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            font-family: sans-serif;
            z-index: 1000;
            max-width: 250px;
        }
        
        .auth-status.authenticated {
            background-color: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
        }
        
        .auth-status.not-authenticated {
            background-color: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }
    </style>
    """
    
    # Add download YAML button
    download_button = """
    <a href="/openapi.yaml?download=true" class="download-yaml-btn" target="_blank">Download OpenAPI Spec</a>
    """
    
    # Add login button
    login_button = """
    <a href="/api/v1/auth/login/google" class="login-btn" target="_blank">Login with Google</a>
    """
    
    # Add auth status display
    auth_status = """
    <div id="auth-status" class="auth-status not-authenticated">
        Not authenticated
    </div>
    """
    
    # Add JavaScript for auth helper
    auth_helper_js = """
    <script>
        // Function to check if user is authenticated
        async function checkAuthStatus() {
            try {
                // Get the token from localStorage
                const token = localStorage.getItem('token');
                
                if (!token) {
                    document.getElementById('auth-status').className = 'auth-status not-authenticated';
                    document.getElementById('auth-status').innerText = 'Not authenticated';
                    return;
                }
                
                // Try to fetch user info
                const response = await fetch('/api/v1/auth/me', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (response.ok) {
                    const userData = await response.json();
                    document.getElementById('auth-status').className = 'auth-status authenticated';
                    document.getElementById('auth-status').innerText = `Authenticated as: ${userData.email} (${userData.role})`;
                    
                    // Auto-fill the Authorize dialog
                    const authorizeBtn = document.querySelector('.btn.authorize');
                    if (authorizeBtn) {
                        authorizeBtn.addEventListener('click', () => {
                            // Wait for the modal to appear
                            setTimeout(() => {
                                const tokenInput = document.querySelector('input[type="text"][data-name="bearerAuth"]');
                                if (tokenInput) {
                                    tokenInput.value = `Bearer ${token}`;
                                }
                            }, 500);
                        });
                    }
                } else {
                    document.getElementById('auth-status').className = 'auth-status not-authenticated';
                    document.getElementById('auth-status').innerText = 'Token invalid or expired';
                    localStorage.removeItem('token');
                }
            } catch (error) {
                console.error('Error checking auth status:', error);
                document.getElementById('auth-status').className = 'auth-status not-authenticated';
                document.getElementById('auth-status').innerText = 'Error checking authentication';
            }
        }
        
        // Check auth status when page loads
        window.addEventListener('load', checkAuthStatus);
        
        // Add listener for message from login page
        window.addEventListener('message', (event) => {
            if (event.data && event.data.token) {
                localStorage.setItem('token', event.data.token);
                checkAuthStatus();
            }
        });
    </script>
    """
    
    # Add Markdown plugin for Swagger UI
    markdown_plugin = """
    <script>
        window.onload = function() {
            // Wait for SwaggerUIBundle to be available
            setTimeout(function() {
                // Enable Markdown rendering for descriptions
                const ui = window.ui;
                if (ui && ui.getConfigs) {
                    const configs = ui.getConfigs();
                    configs.useMarkdownInDescription = true;
                    configs.useMarkdownInResponses = true;
                    configs.useMarkdownInParameters = true;
                    
                    // Force refresh the UI
                    ui.specActions.updateSpec(ui.specSelectors.specStr());
                }
            }, 1000);
        };
    </script>
    """
    
    # Insert our custom elements before the closing body tag
    modified_content = content.replace(
        "</body>",
        f"{custom_css}{download_button}{login_button}{auth_status}{auth_helper_js}{markdown_plugin}</body>"
    )
    
    return HTMLResponse(modified_content)

# Custom ReDoc UI with YAML download button
@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    redoc_html = get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{settings.APP_NAME} - ReDoc",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        with_google_fonts=True
    )
    
    # Convert to string and add our custom button
    content = redoc_html.body.decode("utf-8")
    
    # Add CSS for download button
    download_button_css = """
    <style>
        .download-yaml-btn {
            position: fixed;
            top: 70px;
            right: 20px;
            background-color: #4CAF50;
            color: white !important;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            z-index: 1000;
            font-size: 14px;
            font-family: sans-serif;
        }
        .download-yaml-btn:hover {
            background-color: #45a049;
        }
    </style>
    """
    
    # Add download button
    download_button = """
    <a href="/openapi.yaml?download=true" class="download-yaml-btn">Download YAML</a>
    """
    
    # Insert CSS in head
    content = content.replace("</head>", f"{download_button_css}</head>")
    
    # Insert button after body tag
    content = content.replace("<body>", f"<body>{download_button}")
    
    return HTMLResponse(content=content)

# OAuth2 redirect endpoint for Swagger UI
@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

# Endpoint to download OpenAPI spec as YAML
@app.get("/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml(request: Request):
    import yaml
    from fastapi.responses import Response
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description + """

## Authentication

This API supports two authentication methods:

1. **JWT Bearer Token**: Obtain a token via `/api/v1/auth/login` endpoint
2. **Google OAuth2**: Use the Google login button in the Swagger UI or [login directly](/api/v1/auth/login/google)

### JWT Authentication

1. Use the `/api/v1/auth/login` endpoint with your email and password
2. Copy the returned access token
3. Click the "Authorize" button and enter the token in the format: `Bearer your_token`
4. Or use the "Auto-Authenticate" button after logging in to automatically apply your token

### Google OAuth Authentication

1. Click the "Authorize" button
2. Select "Google OAuth2" and click "Authorize"
3. Complete the Google authentication flow

Alternatively, you can [login with Google directly](/api/v1/auth/login/google) and then return to this page.
""",
        routes=app.routes,
    )
    yaml_content = yaml.dump(openapi_schema)
    
    # Check if the request wants a direct download
    download = request.query_params.get("download")
    
    if download:
        return Response(
            content=yaml_content,
            media_type="text/yaml",
            headers={"Content-Disposition": "attachment; filename=openapi.yaml"}
        )
    
    # Otherwise return HTML page with download link
    return HTMLResponse(
        f"""
        <html>
        <head>
            <title>OpenAPI YAML</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.6;
                    padding: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                pre {{ 
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                    white-space: pre-wrap;
                }}
                .download-btn {{
                    display: inline-block;
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .download-btn:hover {{
                    background-color: #45a049;
                }}
                h1 {{
                    color: #333;
                }}
                .links {{
                    margin-bottom: 20px;
                }}
                .links a {{
                    margin-right: 15px;
                    color: #0066cc;
                    text-decoration: none;
                }}
                .links a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <h1>OpenAPI Specification - YAML Format</h1>
            <div class="links">
                <a href="/docs">Swagger UI</a>
                <a href="/redoc">ReDoc</a>
                <a href="/openapi.json">OpenAPI JSON</a>
            </div>
            <a href="/openapi.yaml?download=true" class="download-btn">Download YAML</a>
            <pre>{yaml_content}</pre>
        </body>
        </html>
        """
    )

# Custom OpenAPI schema with security definitions
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add JWT Bearer security scheme
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token in the format: **Bearer your_token**"
        },
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/api/v1/auth/login",
                    "scopes": {}
                }
            },
            "description": "Standard OAuth2 password flow"
        },
        "googleOAuth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": f"https://accounts.google.com/o/oauth2/auth",
                    "tokenUrl": f"https://oauth2.googleapis.com/token",
                    "scopes": {
                        "openid": "OpenID Connect",
                        "email": "Email address",
                        "profile": "User profile"
                    }
                }
            },
            "description": "Google OAuth2 authentication"
        }
    }
    
    # Apply security globally to all endpoints - use only bearerAuth as the primary method
    # This ensures consistent authorization UI in Swagger
    openapi_schema["security"] = [
        {"bearerAuth": []}
    ]
    
    # Ensure public endpoints don't require authentication
    for path, path_item in openapi_schema.get("paths", {}).items():
        # Skip applying security to login and public endpoints
        if (
            "/auth/login" in path or 
            "/auth/callback" in path or
            "/docs" in path or
            "/redoc" in path or
            "/openapi.json" in path or
            "/openapi.yaml" in path or
            path == "/"
        ):
            # Remove security requirement for these paths
            for method in path_item:
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    path_item[method]["security"] = []
        
        # Ensure auth endpoints that require authentication have proper security requirements
        elif (
            "/auth/me" in path or
            "/auth/logout" in path or
            "/auth/refresh" in path or
            "/auth/set-password" in path
        ):
            # Explicitly set security for these paths
            for method in path_item:
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    path_item[method]["security"] = [{"bearerAuth": []}]
        
        # Add x-markdown extension to enable Markdown rendering for all endpoint descriptions
        for method in path_item:
            if method.lower() in ["get", "post", "put", "delete", "patch"]:
                if "description" in path_item[method]:
                    path_item[method]["x-markdown"] = True
                if "responses" in path_item[method]:
                    for status_code, response in path_item[method]["responses"].items():
                        if "description" in response:
                            response["x-markdown"] = True
    
    # Add x-markdown extension to enable Markdown rendering for the API description
    openapi_schema["info"]["x-markdown"] = True
    
    # Add function declarations to the schema
    openapi_schema["x-function-declarations"] = {
        "functions": function_router.get_function_declarations()
    }
    
    # Add tags with descriptions and ordering
    openapi_schema["tags"] = [
        {"name": "Authentication", "description": "Authentication and user session management endpoints", "x-markdown": True},
        {"name": "User", "description": "User profile and account management endpoints", "x-markdown": True},
        {"name": "monitoring", "description": "System monitoring and health check endpoints", "x-markdown": True},
        {"name": "Courses", "description": "Course management and enrollment endpoints", "x-markdown": True},
        {"name": "User Courses", "description": "User course enrollment and management endpoints", "x-markdown": True},
        {"name": "Faculty Courses", "description": "Faculty course management endpoints", "x-markdown": True},
        {"name": "Assignments", "description": "Assignment creation, submission, and grading endpoints", "x-markdown": True},
        {"name": "Chat", "description": "AI chat and conversation endpoints", "x-markdown": True},
        {"name": "FAQs", "description": "Frequently asked questions management endpoints", "x-markdown": True},
        {"name": "System Settings", "description": "System configuration and settings endpoints", "x-markdown": True},
        {"name": "academic-integrity", "description": "Academic integrity monitoring and management endpoints", "x-markdown": True},
        {"name": "Notification", "description": "User notification endpoints", "x-markdown": True}
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add routers with API prefix
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(user_router, prefix="/api/v1", tags=["User"])
app.include_router(user_routers, prefix="/api/v1", tags=["User Management"])
app.include_router(chat, prefix="/api/v1", tags=["Chat"])
app.include_router(assignment_router, prefix="/api/v1", tags=["Assignments"])
app.include_router(faq_router, tags=["FAQs"])
app.include_router(system_settings_router, prefix="/api/v1", tags=["System Settings"])
# Include both course routers with appropriate tags
app.include_router(courses_router, prefix="/api/v1", tags=["User Courses"])
app.include_router(course_router, prefix="/api/v1", tags=["Faculty Courses"])
app.include_router(academic_integrity_router, prefix="/api/v1")
app.include_router(monitoring.router, prefix="/api/v1")
app.include_router(notification, prefix="/api/v1", tags=["Notification"])

@app.get("/api-login", include_in_schema=False)
async def api_login_page():
    """Serve a custom login page for API documentation"""
    return HTMLResponse(open("app/static/login.html").read())

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENV == "development"
    )
