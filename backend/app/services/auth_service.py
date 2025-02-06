from fastapi import HTTPException, Depends
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from typing import Optional
from app.models.user import User

async def get_current_user(request: Request) -> dict:
    """Get the current authenticated user from session"""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

async def get_or_create_user(db: AsyncSession, user_data: dict) -> Optional[dict]:
    """Get existing user or create a new one"""
    try:
        # Check if user exists
        user = await db.query(User).filter(User.email == user_data.get("email")).first()
        
        if not user:
            # Create new user
            user = User(
                email=user_data.get("email"),
                name=user_data.get("name"),
                picture=user_data.get("picture")
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def require_auth(request: Request):
    """Dependency to check if user is authenticated"""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user
