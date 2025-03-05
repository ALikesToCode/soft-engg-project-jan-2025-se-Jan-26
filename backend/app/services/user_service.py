from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from pydantic import BaseModel, EmailStr
from typing import Optional
import bcrypt

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str = "student" # Default role
    password: str
    picture: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: Optional[str] = None
    picture: Optional[str] = None


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    user_dict = user_data.model_dump(exclude_unset=True)  # Remove unset fields
    user = User(**user_dict)
    user.hashed_password = bcrypt.hashpw(
        user_data.password.encode('utf-8'),
        bcrypt.gensalt()).decode('utf-8')
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_dict = user_data.model_dump(exclude_unset=True)  # Remove unset fields
    if "password" in update_dict:
        update_dict["hashed_password"] = bcrypt.hashpw(
            update_dict.pop("password").encode('utf-8'),
            bcrypt.gensalt()).decode('utf-8')
    for key, value in update_dict.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user_id: int):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}