from app.models.user import init_db
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import os

app = FastAPI()

# Secret key for session middleware
SECRET_KEY = os.getenv("SESSION_SECRET", "your_super_secret_key")

# Add Session Middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Import and include your authentication routes
from app.routes.auth import router as auth_router

app.include_router(auth_router)

@app.on_event("startup")
async def startup():
    await init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
