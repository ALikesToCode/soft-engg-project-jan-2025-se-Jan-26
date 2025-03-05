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
from app.routes.llm import router as chat
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

# Configure logging
logger = configure_logging()
logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

# Get the absolute path to the static directory
STATIC_DIR = Path(__file__).parent / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for application startup and shutdown"""
    # Initialize database on startup
    await init_db()
    
    # Create default users
    async with async_session() as session:
        await create_default_users(session)
    
    # Start monitoring service background tasks
    await monitoring_service.start_background_tasks()
    
    yield
    
    # Stop monitoring service background tasks on shutdown
    await monitoring_service.stop_background_tasks()

# Replace the FastAPI app instance with one that uses the lifespan handler
app = FastAPI(
    title="Support Dashboard API",
    description="API for the support dashboard monitoring system",
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
        
        .auth-helper {
            position: fixed;
            top: 120px;
            right: 20px;
            background-color: #2196F3;
            color: white !important;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            z-index: 1000;
            font-size: 14px;
            font-family: sans-serif;
            cursor: pointer;
        }
        .auth-helper:hover {
            background-color: #0b7dda;
        }
        
        .login-btn {
            position: fixed;
            top: 170px;
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
    
    # Add download button and auth helper button
    custom_buttons = """
    <a href="/openapi.yaml?download=true" class="download-yaml-btn">Download YAML</a>
    <a id="auth-helper-btn" class="auth-helper">Auto-Authenticate</a>
    <a href="/api-login" class="login-btn">Login Page</a>
    <div id="auth-status" class="auth-status not-authenticated">Not authenticated</div>
    """
    
    # Add JavaScript to handle auto-authentication
    auth_script = """
    <script>
        window.addEventListener('load', function() {
            const authStatus = document.getElementById('auth-status');
            
            // Check if token exists and update status
            function updateAuthStatus() {
                const token = localStorage.getItem('token');
                if (token) {
                    authStatus.textContent = 'Authenticated';
                    authStatus.className = 'auth-status authenticated';
                } else {
                    authStatus.textContent = 'Not authenticated';
                    authStatus.className = 'auth-status not-authenticated';
                }
            }
            
            // Initial status check
            updateAuthStatus();
            
            // Add click handler for the auto-authenticate button
            document.getElementById('auth-helper-btn').addEventListener('click', function() {
                // Try to get token from localStorage
                const token = localStorage.getItem('token');
                if (token) {
                    // Find the authorize button and click it
                    const authorizeBtn = document.querySelector('.btn.authorize');
                    if (authorizeBtn) {
                        authorizeBtn.click();
                        
                        // Wait for the modal to appear
                        setTimeout(function() {
                            // Find the bearerAuth input and set the value
                            const inputs = document.querySelectorAll('.auth-container input');
                            for (let input of inputs) {
                                if (input.placeholder === 'Bearer <JWT>' || input.placeholder === 'Bearer <token>') {
                                    input.value = 'Bearer ' + token;
                                    
                                    // Find and click the Authorize button in the modal
                                    const authorizeModalBtn = document.querySelector('.auth-btn-wrapper button.authorize');
                                    if (authorizeModalBtn) {
                                        authorizeModalBtn.click();
                                        
                                        // Find and click the Close button
                                        setTimeout(function() {
                                            const closeBtn = document.querySelector('.btn-done');
                                            if (closeBtn) {
                                                closeBtn.click();
                                                updateAuthStatus();
                                            }
                                        }, 500);
                                    }
                                    break;
                                }
                            }
                        }, 500);
                    }
                } else {
                    alert('No authentication token found in localStorage. Please login first.');
                }
            });
            
            // Intercept fetch/XHR requests to capture the token from login responses
            const originalFetch = window.fetch;
            window.fetch = async function(url, options) {
                const response = await originalFetch(url, options);
                
                // Clone the response to avoid consuming it
                const clone = response.clone();
                
                // Check if this is a login response
                if (url.includes('/api/v1/auth/login') && response.ok) {
                    try {
                        const data = await clone.json();
                        if (data && data.access_token) {
                            localStorage.setItem('token', data.access_token);
                            console.log('Token saved to localStorage');
                            updateAuthStatus();
                        }
                    } catch (e) {
                        console.error('Error processing response:', e);
                    }
                }
                
                return response;
            };
            
            // Add event listener to all operation buttons to ensure they use the latest token
            const observer = new MutationObserver(function(mutations) {
                // Look for operation buttons
                document.querySelectorAll('.opblock-summary-control').forEach(function(button) {
                    if (!button.hasTokenListener) {
                        button.hasTokenListener = true;
                        button.addEventListener('click', function() {
                            // When an operation is clicked, wait for the "Try it out" button to appear
                            setTimeout(function() {
                                const tryItOutBtn = button.closest('.opblock').querySelector('.try-out__btn');
                                if (tryItOutBtn) {
                                    tryItOutBtn.addEventListener('click', function() {
                                        // When "Try it out" is clicked, wait for the Execute button to appear
                                        setTimeout(function() {
                                            const executeBtn = button.closest('.opblock').querySelector('.execute');
                                            if (executeBtn) {
                                                executeBtn.addEventListener('click', function() {
                                                    // When Execute is clicked, ensure the latest token is used
                                                    const token = localStorage.getItem('token');
                                                    if (token) {
                                                        // Find the Authorization header input
                                                        const authHeader = button.closest('.opblock').querySelector('.parameters input[placeholder="Authorization"]');
                                                        if (authHeader && (!authHeader.value || authHeader.value === 'Bearer ')) {
                                                            authHeader.value = 'Bearer ' + token;
                                                        }
                                                    }
                                                });
                                            }
                                        }, 100);
                                    });
                                }
                            }, 100);
                        });
                    }
                });
            });
            
            // Start observing the document for changes
            observer.observe(document.body, { childList: true, subtree: true });
            
            // Auto-authenticate on page load if token exists
            setTimeout(function() {
                const token = localStorage.getItem('token');
                if (token) {
                    document.getElementById('auth-helper-btn').click();
                }
            }, 1000);
        });
    </script>
    """
    
    # Insert CSS in head
    content = content.replace("</head>", f"{custom_css}</head>")
    
    # Insert buttons after body tag
    content = content.replace("<body>", f"<body>{custom_buttons}")
    
    # Insert auth script before end of body
    content = content.replace("</body>", f"{auth_script}</body>")
    
    return HTMLResponse(content=content)

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
        description=app.description,
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
    
    # Add function declarations to the schema
    openapi_schema["x-function-declarations"] = {
        "functions": function_router.get_function_declarations()
    }
    
    # Add tags with descriptions and ordering
    openapi_schema["tags"] = [
        {"name": "Authentication", "description": "Authentication and user session management endpoints"},
        {"name": "User", "description": "User profile and account management endpoints"},
        {"name": "Monitoring", "description": "System monitoring and health check endpoints"},
        {"name": "Courses", "description": "Course management and enrollment endpoints"},
        {"name": "Assignments", "description": "Assignment creation, submission, and grading endpoints"},
        {"name": "Chat", "description": "AI chat and conversation endpoints"},
        {"name": "FAQs", "description": "Frequently asked questions management endpoints"},
        {"name": "System Settings", "description": "System configuration and settings endpoints"}
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add routers with API prefix
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(user_router, prefix="/api/v1", tags=["User"])
app.include_router(chat, prefix="/api/v1", tags=["Chat"])
app.include_router(assignment_router, prefix="/api/v1", tags=["Assignments"])
app.include_router(faq_router, tags=["FAQs"])
app.include_router(system_settings_router, prefix="/api/v1", tags=["System Settings"])
# Include both course routers with appropriate tags
app.include_router(courses_router, prefix="/api/v1", tags=["User Courses"])
app.include_router(course_router, prefix="/api/v1", tags=["Faculty Courses"])
app.include_router(academic_integrity_router, prefix="/api/v1", tags=["Academic Integrity"])
app.include_router(monitoring.router, prefix="/api/v1", tags=["Monitoring"])
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
