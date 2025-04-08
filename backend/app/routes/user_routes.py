from fastapi import APIRouter, HTTPException, Depends, status, Query, Body, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.routes.auth import require_role
# from app.services.auth_service import create_user, update_user, delete_user
from app.services.user_service import create_user, update_user, delete_user, UserCreate, UserUpdate
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User, UserRole
from pydantic import BaseModel, EmailStr, ConfigDict
import bcrypt
import uuid
from typing import List, Optional, Dict, Any
from app.schemas.user_schema import UserOut, UserList, UserChangePassword, UserLogin, UserRegister
from app.services.auth_service import oauth2_scheme, pwd_context as password_context
from app.utils.jwt_utils import create_access_token, decode_access_token
from app.utils.pagination import paginate_results
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import logging
from app.cache import redis_client  # Import Redis client for caching
import re  # For password validation regex
from app.config import settings
import json
import asyncio

# Configure logger for this module
logger = logging.getLogger(__name__)

router = APIRouter(tags=["User Management"])

# Constants from settings
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
JWT_SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM

# Authentication helper functions
def get_password_hash(password: str) -> str:
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.get(User, uuid.UUID(user_id))
    if user is None:
        raise credentials_exception
    return user

async def get_optional_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

class UserSchema(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: str = "student" # Default role
    picture: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# User routes

@router.get("/users", response_model=List[UserSchema], dependencies=[Depends(require_role("support"))])
async def get_users_endpoint(db: AsyncSession = Depends(get_db)):
    users = await db.execute(select(User))
    return users.scalars().all()

@router.post("/users/add", response_model=UserSchema, dependencies=[Depends(require_role("support"))])
async def create_user_endpoint(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user_data)

@router.get("/users/{user_id}", response_model=UserSchema, dependencies=[Depends(require_role("support"))])
async def get_user_endpoint(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserSchema, dependencies=[Depends(require_role("support"))])
async def update_user_endpoint(user_id: uuid.UUID, user_data: UserUpdate, db: AsyncSession = Depends(get_db)):
    return await update_user(db, user_id, user_data)

@router.delete("/users/{user_id}", dependencies=[Depends(require_role("support"))])
async def delete_user_endpoint(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
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

# Password strength regex
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

async def check_user_exists(email: str, db: AsyncSession) -> bool:
    """
    Check if a user with the given email already exists
    
    Args:
        email: Email to check
        db: Database session
        
    Returns:
        bool: True if user exists, False otherwise
    """
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalars().first()
    return user is not None


@router.post("/register", response_model=UserOut, summary="Register a new user")
async def register(user: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Register a new user with email and password
    
    Args:
        user: User data for registration
        db: Database session
        
    Returns:
        UserOut: Newly created user data
        
    Raises:
        HTTPException: If user with email already exists
    """
    # Check if user already exists
    if await check_user_exists(user.email, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    if not re.match(PASSWORD_REGEX, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters and include uppercase, lowercase, numbers, and special characters"
        )
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create new user
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name,
        role=user.role or UserRole.STUDENT,  # Default to STUDENT if not specified
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Log successful registration
    logger.info(f"User registered: {user.email}")
    
    return db_user


@router.post("/login", summary="Login and get access token")
async def login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and generate JWT token
    
    Args:
        user_credentials: User login credentials
        db: Database session
        
    Returns:
        dict: Access token and user data
        
    Raises:
        HTTPException: If login credentials are invalid
    """
    # Get user
    query = select(User).where(User.email == user_credentials.email)
    result = await db.execute(query)
    user = result.scalars().first()
    
    # Verify user and password
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # Log successful login
    logger.info(f"User logged in: {user.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
        }
    }


@router.get("/users", response_model=UserList, summary="Get all users with pagination")
async def get_users(
    response: Response,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users with pagination support
    
    Args:
        response: FastAPI response object for caching headers
        page: Page number (1-indexed)
        per_page: Number of items per page
        role: Filter users by role
        search: Search term for name or email
        current_user: Current authenticated user (must be admin)
        db: Database session
        
    Returns:
        UserList: Paginated list of users
        
    Raises:
        HTTPException: If current user is not an admin
    """
    # Check if user is admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view all users"
        )
    
    # Try to get from cache first
    cache_key = f"users_page_{page}_size_{per_page}_role_{role}_search_{search}"
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        # Set cache header to inform client the response is from cache
        response.headers["X-Cache"] = "HIT"
        return json.loads(cached_data)
    
    # Set cache miss header
    response.headers["X-Cache"] = "MISS"
    
    # Base query
    query = select(User)
    
    # Apply filters
    if role:
        query = query.where(User.role == role)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (User.name.ilike(search_term)) | 
            (User.email.ilike(search_term))
        )
    
    # Get paginated results
    total, items = await paginate_results(db, query, page, per_page)
    
    # Convert to dict for response
    result = {
        "items": [item.to_dict() for item in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page  # Ceiling division
    }
    
    # Cache the result for 5 minutes
    await redis_client.setex(
        cache_key,
        settings.CACHE_EXPIRY_SECONDS,  # Cache for 5 minutes
        json.dumps(result, default=str)
    )
    
    return result


@router.get("/users/me", response_model=UserOut, summary="Get current user profile")
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get the profile of the currently authenticated user"""
    return current_user


@router.get("/users/{user_id}", response_model=UserOut, summary="Get user by ID")
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID (admin or self only)
    
    Args:
        user_id: User ID to retrieve
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserOut: User data
        
    Raises:
        HTTPException: If user not found or not authorized
    """
    # If not admin and not requesting own profile
    if current_user.role != UserRole.ADMIN and str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    # Get user by ID
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/users/{user_id}", response_model=UserOut, summary="Update user")
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user information (admin or self only)
    
    Args:
        user_id: User ID to update
        user_update: Updated user data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserOut: Updated user data
        
    Raises:
        HTTPException: If user not found or not authorized
    """
    # If not admin and not updating own profile
    if current_user.role != UserRole.ADMIN and str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Get user by ID
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields if provided
    if user_update.name is not None:
        user.name = user_update.name
    
    # Only admin can update role
    if user_update.role is not None and current_user.role == UserRole.ADMIN:
        user.role = user_update.role
    
    # Update database
    await db.commit()
    await db.refresh(user)
    
    # Invalidate cache
    await redis_client.delete(f"user_{user_id}")
    await redis_client.delete(f"users_page_*")  # Clear all user listings
    
    # Log update
    logger.info(f"User updated: {user.email} by {current_user.email}")
    
    return user


@router.post("/users/change-password", status_code=status.HTTP_200_OK, summary="Change password")
async def change_password(
    password_change: UserChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password (requires current password)
    
    Args:
        password_change: Old and new password
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If current password is incorrect or new password is invalid
    """
    # Verify current password
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Validate new password strength
    if not re.match(PASSWORD_REGEX, password_change.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters and include uppercase, lowercase, numbers, and special characters"
        )
    
    # Hash and update password
    current_user.hashed_password = get_password_hash(password_change.new_password)
    
    # Update database
    await db.commit()
    
    # Log password change (without revealing password)
    logger.info(f"Password changed for user: {current_user.email}")
    
    return {"message": "Password updated successfully"}


@router.post("/users/batch", status_code=status.HTTP_200_OK, summary="Batch user operations")
async def batch_user_operations(
    operations: Dict[str, List[Dict[str, Any]]] = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform batch operations on users (admin only)
    
    Args:
        operations: Dictionary with keys 'create', 'update', 'delete' 
                   containing lists of operations
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Results of batch operations
        
    Raises:
        HTTPException: If user is not an admin
    """
    # Check if user is admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform batch operations"
        )
    
    results = {
        "created": [],
        "updated": [],
        "deleted": [],
        "errors": []
    }
    
    # Process create operations
    for create_op in operations.get("create", []):
        try:
            # Check if user exists
            if await check_user_exists(create_op.get("email"), db):
                results["errors"].append({
                    "operation": "create",
                    "data": create_op,
                    "error": "Email already registered"
                })
                continue
            
            # Create user
            hashed_password = get_password_hash(create_op.get("password", "ChangeMe123!"))
            
            new_user = User(
                email=create_op.get("email"),
                name=create_op.get("name"),
                role=create_op.get("role", UserRole.STUDENT),
                hashed_password=hashed_password
            )
            
            db.add(new_user)
            await db.flush()  # Flush to get ID without committing transaction
            
            results["created"].append({
                "id": str(new_user.id),
                "email": new_user.email,
                "name": new_user.name,
                "role": new_user.role
            })
            
        except Exception as e:
            results["errors"].append({
                "operation": "create",
                "data": create_op,
                "error": str(e)
            })
    
    # Process update operations
    for update_op in operations.get("update", []):
        try:
            user_id = update_op.get("id")
            if not user_id:
                results["errors"].append({
                    "operation": "update",
                    "data": update_op,
                    "error": "Missing user ID"
                })
                continue
            
            # Get user
            query = select(User).where(User.id == user_id)
            result = await db.execute(query)
            user = result.scalars().first()
            
            if not user:
                results["errors"].append({
                    "operation": "update",
                    "data": update_op,
                    "error": "User not found"
                })
                continue
            
            # Update fields
            if "name" in update_op:
                user.name = update_op["name"]
            
            if "role" in update_op:
                user.role = update_op["role"]
            
            if "password" in update_op:
                user.hashed_password = get_password_hash(update_op["password"])
            
            await db.flush()
            
            results["updated"].append({
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role
            })
            
        except Exception as e:
            results["errors"].append({
                "operation": "update",
                "data": update_op,
                "error": str(e)
            })
    
    # Process delete operations
    for delete_op in operations.get("delete", []):
        try:
            user_id = delete_op.get("id")
            if not user_id:
                results["errors"].append({
                    "operation": "delete",
                    "data": delete_op,
                    "error": "Missing user ID"
                })
                continue
            
            # Get user
            query = select(User).where(User.id == user_id)
            result = await db.execute(query)
            user = result.scalars().first()
            
            if not user:
                results["errors"].append({
                    "operation": "delete",
                    "data": delete_op,
                    "error": "User not found"
                })
                continue
            
            # Don't allow deleting yourself
            if str(user.id) == str(current_user.id):
                results["errors"].append({
                    "operation": "delete",
                    "data": delete_op,
                    "error": "Cannot delete your own account"
                })
                continue
            
            # Store info before deletion for response
            user_info = {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
            
            # Delete user
            await db.delete(user)
            
            results["deleted"].append(user_info)
            
        except Exception as e:
            results["errors"].append({
                "operation": "delete",
                "data": delete_op,
                "error": str(e)
            })
    
    # Commit all changes
    await db.commit()
    
    # Invalidate cache
    await redis_client.delete("users_page_*")  # Clear all user listings
    
    # Log batch operation
    logger.info(f"Batch user operations performed by {current_user.email}: " 
                f"Created: {len(results['created'])}, " 
                f"Updated: {len(results['updated'])}, " 
                f"Deleted: {len(results['deleted'])}, " 
                f"Errors: {len(results['errors'])}")
    
    return results


# Initialize admin user if doesn't exist
async def init_admin_user():
    """Create admin user if it doesn't exist"""
    async def _create_admin():
        async with get_db() as db:
            # Check if any admin exists
            query = select(User).where(User.role == UserRole.ADMIN)
            result = await db.execute(query)
            admin = result.scalars().first()
            
            if not admin:
                # Create admin user
                hashed_password = get_password_hash(settings.ADMIN_DEFAULT_PASSWORD)
                admin_user = User(
                    email=settings.ADMIN_EMAIL,
                    name="System Administrator",
                    role=UserRole.ADMIN,
                    hashed_password=hashed_password
                )
                db.add(admin_user)
                await db.commit()
                logger.info("Admin user created")
    
    # Create admin in background after startup
    asyncio.create_task(_create_admin())