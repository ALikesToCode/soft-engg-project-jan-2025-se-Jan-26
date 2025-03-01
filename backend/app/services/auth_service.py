from fastapi import HTTPException, Depends
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.utils.jwt_utils import create_access_token, decode_access_token
import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_user(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def authenticate_user(db: AsyncSession, email: str, password: str): # -> Optional[User]:
    """
    Authenticate a user by email and password.
    Returns the user if authenticated, otherwise returns None.
    """
    try:
        # Fetch the user by email
        user = await get_user(db, email)
        if not user or not user.is_google_user:
            return False
        # Check if the user exists and the password is correct
        if not bcrypt.checkpw(password.encode("utf-8"), user.hashed_password):
            return False
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_or_create_user(db: AsyncSession, user_data: dict) -> User:
    """
    Retrieve an existing user by email, or create a new one if not found.
    The new user is populated with data from the provided user_data dictionary.
    """
    try:
        # Attempt to fetch an existing user by email
        user = await get_user(db, user_data.get("email"))

        if user:
            print("User already exists")
            return user
        else:
            print("Creating new user")
            # Create a new user using available fields
            new_user = User(
                # first_name=user_data.get("given_name"),
                # last_name=user_data.get("family_name"),
                email=user_data.get("email"),
                picture=user_data.get("picture"),
                name=user_data.get("name"),
                hashed_password="",
                is_google_user=True,
            )
            db.add(new_user)
            await db.commit()  # Commit changes to the database
            await db.refresh(new_user)  # Refresh the instance to load new data (e.g., generated ID)
            return new_user
            
    except Exception as e:
        await db.rollback()  # Rollback in case of any error
        raise HTTPException(status_code=500, detail=str(e))

# async def get_current_user(request: Request) -> dict:
#     """
#     Retrieve the current authenticated user from the session.
#     Raises a 401 HTTPException if no user is found in the session.
#     """
#     user = request.session.get("user")
#     if not user:
#         raise HTTPException(status_code=401, detail="Not authenticated")
#     return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current user from the provided JWT token.
    Raises a 401 HTTPException if the token is invalid or expired.
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload # this returns the payload of the token containing email and role

def require_auth(token: str = Depends(oauth2_scheme)):
    """
    Dependency that enforces authentication by ensuring a user exists in the session.
    Raises a 401 HTTPException if the user is not authenticated.
    """
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

# def require_auth(request: Request):
#     """
#     Dependency that enforces authentication by ensuring a user exists in the session.
#     Raises a 401 HTTPException if the user is not authenticated.
#     """
#     user = request.session.get("user")
#     if not user:
#         raise HTTPException(status_code=401, detail="Authentication required")
#     return user
