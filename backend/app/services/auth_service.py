from fastapi import HTTPException, Depends
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, Callable
from app.database import get_db
from app.models.user import User
from app.utils.jwt_utils import create_access_token, decode_access_token
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import logging
import uuid
from datetime import datetime, UTC

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="bearerAuth"  # Match the scheme name in OpenAPI schema
)
pwd_context = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto',
    bcrypt__rounds=12,
    bcrypt__ident='2b'
)

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
    try:
        from sqlalchemy import text
        
        # Use direct SQL query to avoid ORM mapping issues
        result = await db.execute(
            text("SELECT id, email, name, hashed_password, is_google_user, picture, created_at, updated_at, role FROM users WHERE email = :email"),
            {"email": email}
        )
        
        row = result.fetchone()
        if not row:
            return None
            
        # Create a User object from the row
        user = User(
            id=row.id,
            email=row.email,
            name=row.name,
            hashed_password=row.hashed_password,
            is_google_user=row.is_google_user,
            picture=row.picture,
            role=row.role
        )
            
        return user
    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        return None

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
        The User object if authentication is successful, otherwise None
        
    Raises:
        HTTPException: If an error occurs during authentication
    """
    try:
        # Use direct SQL query to avoid ORM mapping issues
        from sqlalchemy import text
        
        # Fetch the user by email using raw SQL
        logger.info(f"Authenticating user: {email}")
        result = await db.execute(
            text("SELECT id, email, name, hashed_password, is_google_user, picture, created_at, updated_at, role FROM users WHERE email = :email"),
            {"email": email}
        )
        
        row = result.fetchone()
        if not row:
            logger.warning(f"User not found: {email}")
            return None
            
        # If user has no password set (Google user without password)
        if not row.hashed_password:
            return None
            
        # Check if the password is correct using passlib
        if not pwd_context.verify(password, row.hashed_password):
            return None
        
        # Create a User object from the row
        user = User(
            id=row.id,
            email=row.email,
            name=row.name,
            hashed_password=row.hashed_password,
            is_google_user=row.is_google_user,
            picture=row.picture,
            role=row.role
        )
            
        return user
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
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
        from sqlalchemy import text
        
        # Attempt to fetch an existing user by email
        email = user_data.get("email")
        user = await get_user(db, email)

        if user:
            print(f"User already exists: {email}")
            
            # Update the user's picture if they're logging in with Google and have a profile picture
            picture_url = user_data.get("picture")
            if picture_url and (user.picture is None or user.picture != picture_url):
                print(f"Updating profile picture for user: {email}")
                await db.execute(
                    text("UPDATE users SET picture = :picture WHERE email = :email"),
                    {"picture": picture_url, "email": email}
                )
                await db.commit()
                
                # Update the user object
                user.picture = picture_url
                
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
            
            # Create a new user using direct SQL
            user_id = uuid.uuid4()
            now = datetime.now(UTC)
            
            await db.execute(
                text("""
                    INSERT INTO users (id, email, name, hashed_password, is_google_user, picture, role, created_at, updated_at)
                    VALUES (:id, :email, :name, :hashed_password, :is_google_user, :picture, :role, :created_at, :updated_at)
                """),
                {
                    "id": user_id,
                    "email": email,
                    "name": user_data.get("name", email.split("@")[0]),
                    "hashed_password": "",
                    "is_google_user": True,
                    "picture": user_data.get("picture"),
                    "role": role,
                    "created_at": now,
                    "updated_at": now
                }
            )
            await db.commit()
            
            # Create and return a User object
            new_user = User(
                id=user_id,
                email=email,
                name=user_data.get("name", email.split("@")[0]),
                hashed_password="",
                is_google_user=True,
                picture=user_data.get("picture"),
                role=role,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return new_user
            
    except Exception as e:
        logger.error(f"Error in get_or_create_user: {str(e)}")
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

async def get_current_faculty(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Get the current user and verify they have faculty role.
    
    This function extends get_current_user by adding a role check to ensure
    the authenticated user has faculty privileges. It's used as a dependency
    in routes that should only be accessible to faculty members.
    
    Args:
        token: The JWT token from the Authorization header
        
    Returns:
        Dictionary containing the user information from the token
        
    Raises:
        HTTPException: If the token is invalid or the user is not a faculty member
    """
    user = await get_current_user(token)
    if user.get("role") != "faculty" and user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Faculty role required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_admin_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Get the current user and verify they have admin role.
    
    This function extends get_current_user by adding a role check to ensure
    the authenticated user has admin privileges. It's used as a dependency
    in routes that should only be accessible to administrators.
    
    Args:
        token: The JWT token from the Authorization header
        
    Returns:
        Dictionary containing the user information from the token
        
    Raises:
        HTTPException: If the token is invalid or the user is not an admin
    """
    user = await get_current_user(token)
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin role required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def require_auth(token: str = Depends(oauth2_scheme)) -> dict:
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
    user = await get_current_user(token)
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
        from sqlalchemy import text
        
        # Check if the user exists
        result = await db.execute(
            text("SELECT id FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        )
        
        if not result.fetchone():
            return False
            
        # Hash the password
        hashed_password = pwd_context.hash(password)
        
        # Update the user's password using direct SQL
        await db.execute(
            text("UPDATE users SET hashed_password = :hashed_password WHERE id = :user_id"),
            {"hashed_password": hashed_password, "user_id": user_id}
        )
        
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"Error setting user password: {str(e)}")
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
        from sqlalchemy import text
        
        # First check if the users table exists
        try:
            # Check if the users table exists
            table_exists = False
            try:
                async with db.begin():
                    result = await db.execute(text(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
                    ))
                    table_exists = result.scalar()
            except Exception as e:
                logger.error(f"Error checking if users table exists: {e}")
                return
                
            if not table_exists:
                logger.warning("Users table does not exist yet. Skipping default user creation.")
                return
                
            # Check if support user exists
            support_email = "support@study.iitm.ac.in"
            result = await db.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": support_email}
            )
            
            support_user = result.fetchone()
            
            if not support_user:
                # Create support user
                logger.info(f"Creating support user {support_email}")
                hashed_password = pwd_context.hash("support123")
                
                now = datetime.now(UTC)
                
                # Use direct SQL to avoid ORM issues
                support_id = str(uuid.uuid4())
                await db.execute(
                    text("""
                        INSERT INTO users (id, email, name, hashed_password, is_google_user, role, created_at, updated_at) 
                        VALUES (:id, :email, :name, :password, :is_google, :role, :created_at, :updated_at)
                    """),
                    {
                        "id": support_id,
                        "email": support_email,
                        "name": "Default Support",
                        "password": hashed_password,
                        "is_google": False,
                        "role": "support",
                        "created_at": now,
                        "updated_at": now
                    }
                )
                print(f"Created default support user: {support_email}")
            
            # Check if faculty user exists
            faculty_email = "faculty@study.iitm.ac.in"
            result = await db.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": faculty_email}
            )
            
            faculty_user = result.fetchone()
            
            if not faculty_user:
                # Create faculty user
                logger.info(f"Creating faculty user {faculty_email}")
                hashed_password = pwd_context.hash("faculty123")
                
                now = datetime.now(UTC)
                
                # Use direct SQL to avoid ORM issues
                faculty_id = str(uuid.uuid4())
                await db.execute(
                    text("""
                        INSERT INTO users (id, email, name, hashed_password, is_google_user, role, created_at, updated_at) 
                        VALUES (:id, :email, :name, :password, :is_google, :role, :created_at, :updated_at)
                    """),
                    {
                        "id": faculty_id,
                        "email": faculty_email,
                        "name": "Default Faculty",
                        "password": hashed_password,
                        "is_google": False,
                        "role": "faculty",
                        "created_at": now,
                        "updated_at": now
                    }
                )
                print(f"Created default faculty user: {faculty_email}")
            
            # Commit changes
            await db.commit()
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error in user creation transaction: {e}")
            
    except Exception as e:
        logger.error(f"Failed to create default users: {e}")

def require_role(required_role):
    """
    Create a dependency that requires a specific role or one of multiple roles.
    
    This function returns a dependency that checks if the current user has
    the required role(s). It's used to protect routes that should only be
    accessible to users with specific roles.
    
    Args:
        required_role: The role or list of roles required to access the route
        
    Returns:
        A dependency function that validates the user's role
        
    Raises:
        HTTPException: If the user doesn't have the required role
    """
    async def role_checker(token: str = Depends(oauth2_scheme)) -> dict:
        user = await get_current_user(token)
        user_role = user.get("role", "").lower()
        
        if isinstance(required_role, list):
            # Check if user role is in the list of required roles
            if user_role not in [r.lower() for r in required_role]:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required roles: {', '.join(required_role)}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            # Check against a single required role
            if user_role != required_role.lower():
                raise HTTPException(
                    status_code=403,
                    detail=f"{required_role} role required",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        return user
    return role_checker
