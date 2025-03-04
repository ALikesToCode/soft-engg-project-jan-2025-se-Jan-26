from app.models.user import User
from app.models.course import Course
from app.database import init_db
from fastapi import FastAPI, Depends
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from fastapi.responses import JSONResponse, HTMLResponse
from app.services.auth_service import create_default_users
from app.database import get_db, async_session
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_service import oauth2_scheme
from starlette.requests import Request
from app.routes.auth import router as auth_router
from app.routes.user import router as user_router
from app.routes.llm import router as chat
from app.routes.assignment import router as assignment_router
from app.routes.faq import router as faq_router
from app.routes.system_settings import router as system_settings_router
from app.routes.courses import router as courses_router
from app.routes.course_routes import course_router

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    # Disable default docs to use custom endpoints
    docs_url=None,
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect"
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

@app.get("/")
async def root():
    return JSONResponse({
        "message": "Welcome to SE Team 26 API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi_json": "/openapi.json",
        "openapi_yaml": "/openapi.yaml",
        "status": "operational",
        "environment": settings.ENV,
        "api_prefix": settings.API_PREFIX
    })

# Custom Swagger UI with OAuth2 support
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        init_oauth={
            "clientId": settings.GOOGLE_CLIENT_ID,
            "clientSecret": settings.GOOGLE_CLIENT_SECRET,
            "appName": settings.APP_NAME,
            "usePkceWithAuthorizationCodeGrant": True,
            "scopes": ["openid", "email", "profile"],
            "useBasicAuthenticationWithAccessCodeGrant": True
        },
        swagger_ui_parameters={
            "persistAuthorization": True,
            "displayRequestDuration": True,
            "filter": True,
            "tryItOutEnabled": True,
            "syntaxHighlight": {
                "activate": True,
                "theme": "agate"
            },
            "oauth2RedirectUrl": f"{settings.FRONTEND_URL}/docs/oauth2-redirect"
        }
    )

# OAuth2 redirect endpoint for Swagger UI
@app.get("/docs/oauth2-redirect", include_in_schema=False)
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
    
    # Apply security globally to all endpoints
    openapi_schema["security"] = [
        {"bearerAuth": []},
        {"googleOAuth2": ["openid", "email", "profile"]}
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add routers with API prefix
app.include_router(auth_router, prefix=settings.API_PREFIX, tags=["Authentication"])
app.include_router(user_router, prefix=settings.API_PREFIX, tags=["User"])
app.include_router(chat, prefix=settings.API_PREFIX, tags=["Chat"])
app.include_router(assignment_router, prefix=settings.API_PREFIX, tags=["Assignments"])
app.include_router(faq_router, tags=["FAQs"])
app.include_router(system_settings_router, prefix=settings.API_PREFIX, tags=["System Settings"])
app.include_router(courses_router, prefix=settings.API_PREFIX, tags=["Courses"])
app.include_router(course_router, prefix=settings.API_PREFIX, tags=["Courses"])

@app.on_event("startup")
async def startup():
    await init_db()
    
    # Create default users
    async with async_session() as session:
        await create_default_users(session)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENV == "development"
    )
