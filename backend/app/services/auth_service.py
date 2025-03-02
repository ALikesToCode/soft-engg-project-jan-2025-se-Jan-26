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

async def get_user(db: AsyncSession, email: str) -> Optional[User]:
    """
    Retrieve a user by email address.
    
    This function queries the database for a user with the specified email address.
    
    Args:
        db: The database session
        email: The email address to search for
        
    Returns:
        The User object if found, otherwise None
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    This function verifies that a user exists with the given email address and that
    the provided password matches the stored hashed password. It handles both
    traditional email/password authentication and Google OAuth users.
    
    Args:
        db: The database session
        email: The user's email address
        password: The plaintext password to verify
        
    Returns:
        The User object if authentication is successful, otherwise False
        
    Raises:
        HTTPException: If an error occurs during authentication
    """
    try:
        # Fetch the user by email
        user = await get_user(db, email)
        if not user:
            return False
            
        # If user has no password set (Google user without password)
        if not user.hashed_password:
            return False
            
        # Check if the password is correct
        if not bcrypt.checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8")):
            return False
            
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_or_create_user(db: AsyncSession, user_data: dict) -> User:
    """
    Retrieve an existing user by email, or create a new one if not found.
    
    This function is primarily used during OAuth authentication to either retrieve
    an existing user account or create a new one based on the profile data from
    the OAuth provider (e.g., Google).
    
    The function assigns roles based on email domain:
    - *@ds.study.iitm.ac.in: student
    - *@study.iitm.ac.in: support (can be changed to faculty later)
    - others: student (default)
    
    Args:
        db: The database session
        user_data: Dictionary containing user profile data from OAuth provider
            (must include at least 'email', may include 'name' and 'picture')
            
    Returns:
        The existing or newly created User object
        
    Raises:
        HTTPException: If an error occurs during user creation or retrieval
    """
    try:
        # Attempt to fetch an existing user by email
        email = user_data.get("email")
        user = await get_user(db, email)

        if user:
            print(f"User already exists: {email}")
            return user
        else:
            print(f"Creating new user: {email}")
            
            # Determine role based on email domain
            role = "student"  # Default role
            
            if email:
                if email.endswith("@ds.study.iitm.ac.in"):
                    role = "student"
                elif email.endswith("@study.iitm.ac.in"):
                    role = "support"
            
            # Create a new user using available fields
            new_user = User(
                email=email,
                picture=user_data.get("picture"),
                name=user_data.get("name"),
                hashed_password="",
                is_google_user=True,
                role=role
            )
            db.add(new_user)
            await db.commit()  # Commit changes to the database
            await db.refresh(new_user)  # Refresh the instance to load new data
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

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Get the current user from the provided JWT token.
    
    This function decodes and validates the JWT token to extract the user information.
    It's typically used as a dependency in protected routes to ensure the request
    is authenticated and to provide user context.
    
    Args:
        token: The JWT token from the Authorization header
        
    Returns:
        Dictionary containing the decoded token payload with user information
        
    Raises:
        HTTPException: If the token is invalid, expired, or missing
    """
    # Handle case where token includes 'Bearer ' prefix
    if token.startswith('Bearer '):
        token = token[7:]
        
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=401, 
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload # this returns the payload of the token containing email and role

def require_auth(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency that enforces authentication by ensuring a valid JWT token.
    
    This function is used as a FastAPI dependency to protect routes that require
    authentication. It validates the JWT token and returns the user information
    if authentication is successful.
    
    Args:
        token: The JWT token from the Authorization header
        
    Returns:
        Dictionary containing the user information from the token
        
    Raises:
        HTTPException: If authentication fails or the token is invalid
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

async def set_user_password(db: AsyncSession, user_id: str, password: str) -> bool:
    """
    Set or update a password for a user.
    
    This function is used to set a password for users who initially authenticated
    via OAuth (e.g., Google) and want to add password authentication as an option.
    It can also be used to update an existing password.
    
    The password is securely hashed using bcrypt before storage.
    
    Args:
        db: The database session
        user_id: The UUID of the user
        password: The new plaintext password to set
        
    Returns:
        True if the password was successfully set, False if the user was not found
        
    Raises:
        HTTPException: If an error occurs during the password update
    """
    try:
        # Find the user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        
        if not user:
            return False
            
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        # Update the user's password
        user.hashed_password = hashed_password
        
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def create_default_users(db: AsyncSession) -> None:
    """
    Create default support and faculty users if they don't exist.
    
    This function is typically called during application startup to ensure
    that default administrative users exist in the system. It creates:
    1. A support user with email 'support@study.iitm.ac.in'
    2. A faculty user with email 'faculty@study.iitm.ac.in'
    
    Both users are created with predefined passwords if they don't already exist.
    
    Args:
        db: The database session
        
    Returns:
        None
        
    Note:
        This function catches and logs exceptions but does not propagate them,
        to prevent application startup failures.
    """
    try:
        # Check if support user exists
        support_email = "support@study.iitm.ac.in"
        support_user = await get_user(db, support_email)
        
        if not support_user:
            # Create support user
            support_user = User(
                email=support_email,
                name="Support Admin",
                hashed_password=bcrypt.hashpw("support123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                is_google_user=False,
                role="support"
            )
            db.add(support_user)
            print(f"Created default support user: {support_email}")
        
        # Check if faculty user exists
        faculty_email = "faculty@study.iitm.ac.in"
        faculty_user = await get_user(db, faculty_email)
        
        if not faculty_user:
            # Create faculty user
            faculty_user = User(
                email=faculty_email,
                name="Faculty Admin",
                hashed_password=bcrypt.hashpw("faculty123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                is_google_user=False,
                role="faculty"
            )
            db.add(faculty_user)
            print(f"Created default faculty user: {faculty_email}")
        
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"Error creating default users: {str(e)}")
