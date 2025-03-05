from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.routes.auth import require_role
# from app.services.auth_service import create_user, update_user, delete_user
from app.services.user_service import create_user, update_user, delete_user, UserCreate, UserUpdate
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from pydantic import BaseModel, EmailStr
import bcrypt
from typing import List, Optional

router = APIRouter()

class UserSchema(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str = "student" # Default role
    picture: Optional[str] = None
    
    class Config:
        from_attributes = True

# User routes

@router.get("/users", response_model=List[UserSchema], dependencies=[Depends(require_role("support"))])
async def get_users_endpoint(db: AsyncSession = Depends(get_db)):
    users = await db.execute(select(User))
    return users.scalars().all()

@router.post("/users/add", response_model=UserSchema, dependencies=[Depends(require_role("support"))])
async def create_user_endpoint(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user_data)

@router.get("/users/{user_id}", response_model=UserSchema, dependencies=[Depends(require_role("support"))])
async def get_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserSchema, dependencies=[Depends(require_role("support"))])
async def update_user_endpoint(user_id: int, user_data: UserUpdate, db: AsyncSession = Depends(get_db)):
    return await update_user(db, user_id, user_data)

@router.delete("/users/{user_id}", dependencies=[Depends(require_role("support"))])
async def delete_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_user(db, user_id)

@router.post("/users/verify-email", dependencies=[Depends(require_role("support"))])
async def verify_email_endpoint(email: str, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # user.is_verified = True
    # await db.commit()
    return {"message": "Email verified"}

@router.post("/users/reset-password", dependencies=[Depends(require_role("support"))]) #Depends(get_current_user), 
async def reset_password_endpoint(email: str, new_password: str, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    await db.commit()
    return {"message": "Password reset"}