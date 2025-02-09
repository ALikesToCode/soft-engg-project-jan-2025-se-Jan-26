from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from app.database import get_db
from app.services.auth_service import get_current_user, require_auth
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class UserProfileUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    picture: str | None = None

@router.get("/user/profile")
async def get_user_profile(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """Get the current user's profile"""
    return user

@router.put("/user/profile")
async def update_user_profile(
    profile_update: UserProfileUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """Update the current user's profile"""
    # Update only provided fields
    for field, value in profile_update.dict(exclude_unset=True).items():
        if value is not None:
            user[field] = value
    
    request.session["user"] = user
    return user
