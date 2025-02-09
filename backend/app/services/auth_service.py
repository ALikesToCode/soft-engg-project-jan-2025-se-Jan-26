from fastapi import HTTPException, Depends
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from app.database import get_db
from app.models.user import User

async def get_or_create_user(db: AsyncSession, user_data: dict) -> User:
    """
    Retrieve an existing user by email, or create a new one if not found.
    The new user is populated with data from the provided user_data dictionary.
    """
    try:
        # Attempt to fetch an existing user by email
        result = await db.execute(select(User).where(User.email == user_data["email"]))
        user = result.scalars().first()  # Get the first matching user, if any

        if user:
            print("User already exists")
            return user
        else:
            print("Creating new user")
            # Create a new user using available fields
            new_user = User(
                first_name=user_data.get("given_name"),
                last_name=user_data.get("family_name"),
                email=user_data.get("email"),
                picture=user_data.get("picture"),
                name=user_data.get("name"),
                at_hash=user_data.get("at_hash")
            )
            db.add(new_user)
            await db.commit()  # Commit changes to the database
            await db.refresh(new_user)  # Refresh the instance to load new data (e.g., generated ID)
            return new_user
    except Exception as e:
        await db.rollback()  # Rollback in case of any error
        raise HTTPException(status_code=500, detail=str(e))

async def get_current_user(request: Request) -> dict:
    """
    Retrieve the current authenticated user from the session.
    Raises a 401 HTTPException if no user is found in the session.
    """
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def require_auth(request: Request):
    """
    Dependency that enforces authentication by ensuring a user exists in the session.
    Raises a 401 HTTPException if the user is not authenticated.
    """
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user
