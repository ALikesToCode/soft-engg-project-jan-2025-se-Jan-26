"""
Simple script to test the available-functions endpoint.
"""
from fastapi import FastAPI
from app.routes.chat import router as chat_router
from app.services.api_functions import *  # Import all API function declarations

# Create a minimal FastAPI app
app = FastAPI()

# Mount the chat router at /api/v1/chat
app.include_router(chat_router, prefix="/api/v1/chat")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 