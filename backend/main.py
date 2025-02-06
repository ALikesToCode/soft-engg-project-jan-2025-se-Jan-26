from app.models.user import init_db
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
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

# Import and include your authentication routes
from app.routes.auth import router as auth_router
from app.routes.user import router as user_router

# Add routers with API prefix
app.include_router(auth_router, prefix=settings.API_PREFIX, tags=["Authentication"])
app.include_router(user_router, prefix=settings.API_PREFIX, tags=["User"])

@app.on_event("startup")
async def startup():
    await init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENV == "development"
    )
