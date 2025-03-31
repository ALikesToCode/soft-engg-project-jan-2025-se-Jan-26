from app.services.auth_service import authenticate_user, get_or_create_user, get_current_user, oauth2_scheme, set_user_password
from app.database import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.jwt_utils import create_access_token, decode_access_token, SECRET_KEY, ALGORITHM
from fastapi import APIRouter, Depends, HTTPException
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request
import redis
from ..config import settings
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from starlette.responses import RedirectResponse
import jwt
from pydantic import BaseModel, ConfigDict
import os
from urllib.parse import urlparse

router = APIRouter(tags=["Authentication"])
logger = logging.getLogger(__name__)

# Check if we're in a serverless environment
SERVERLESS_ENV = os.environ.get("VERCEL") == "1"

# Use settings for Redis configuration if available, otherwise use defaults
redis_host = getattr(settings, 'REDIS_HOST', '127.0.0.1')
redis_port = getattr(settings, 'REDIS_PORT', 6379)
redis_db = getattr(settings, 'REDIS_DB', 0)
redis_url = os.environ.get("REDIS_URL", getattr(settings, 'REDIS_URL', None))
redis_username = getattr(settings, 'REDIS_USERNAME', 'default')
redis_password = getattr(settings, 'REDIS_PASSWORD', None)

# Create a mock Redis client for fallback
class MockRedis:
    def __init__(self):
        self.blacklist = {}
        logger.info("Using in-memory blacklist as Redis fallback")
        
    def exists(self, key):
        return key in self.blacklist
        
    def set(self, key, value, **kwargs):
        self.blacklist[key] = value
        return True
        
    def ping(self):
        return True

# Initialize Redis client with error handling
if SERVERLESS_ENV:
    # In serverless environments, default to using the mock Redis
    # unless a valid REDIS_URL environment variable is provided
    if redis_url:
        try:
            # If we have a URL but no explicit password in it, try to add it
            if redis_password and "://:@" not in redis_url and "@" not in redis_url:
                # Parse the URL to insert password
                parsed = urlparse(redis_url)
                if redis_username != 'default':
                    redis_url = f"{parsed.scheme}://{redis_username}:{redis_password}@{parsed.netloc}{parsed.path}"
                else:
                    redis_url = f"{parsed.scheme}://:{redis_password}@{parsed.netloc}{parsed.path}"
            
            redis_client = redis.from_url(redis_url, decode_responses=True)
            redis_client.ping()
            logger.info("Redis connection established successfully using REDIS_URL")
        except (redis.ConnectionError, redis.exceptions.ResponseError, redis.exceptions.RedisError) as e:
            logger.warning(f"Redis connection failed: {str(e)}. Using fallback mode.")
            redis_client = MockRedis()
    else:
        logger.warning("No REDIS_URL provided in serverless environment. Using in-memory fallback.")
        redis_client = MockRedis()
else:
    # In non-serverless environments, try to connect to Redis using host/port
    try:
        # Include password if available
        connection_kwargs = {
            "host": redis_host,
            "port": redis_port,
            "db": redis_db,
            "decode_responses": True
        }
        
        if redis_username != 'default':
            connection_kwargs["username"] = redis_username
            
        if redis_password:
            connection_kwargs["password"] = redis_password
            
        redis_client = redis.Redis(**connection_kwargs)
        # Test connection
        redis_client.ping()
        logger.info("Redis connection established successfully")
    except (redis.ConnectionError, redis.exceptions.ResponseError, redis.exceptions.RedisError) as e:
        logger.warning(f"Redis connection failed: {str(e)}. Using fallback mode.")
        redis_client = MockRedis()

def is_token_blacklisted(token: str):
    logger = logging.getLogger(__name__)
    try:
        is_blacklisted = redis_client.exists(f'blacklist:{token}')
        if is_blacklisted:
            logger.warning(f"Token is blacklisted: {token[:10]}...")
        return is_blacklisted
    except Exception as e:
        logger.error(f"Error checking token blacklist: {str(e)}")
        # If there's an error checking the blacklist, assume token is not blacklisted
        # This is a fallback to prevent users from being locked out
        return False

def is_token_valid(token: str):
    logger = logging.getLogger(__name__)
    
    if not token:
        logger.error("Empty token provided to is_token_valid")
        return False
        
    # Check if token is blacklisted
    if is_token_blacklisted(token):
        logger.error(f"Token is blacklisted: {token[:10]}...")
        return False
    
    # Decode and validate token
    payload = decode_access_token(token)
    if not payload:
        logger.error(f"Failed to decode token: {token[:10]}...")
        return False
        
    logger.info(f"Token is valid: {token[:10]}...")
    return True

# Initialize OAuth
config = Config(".env")
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    # authorize_params={"scope": "openid email profile"},
    authorize_params = None,
    access_token_url="https://oauth2.googleapis.com/token",
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri="http://localhost:8000/auth/callback",
    userinfo_url="https://www.googleapis.com/oauth2/v3/userinfo",
    client_kwargs={"scope": "openid email profile"},
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
)

# Step 1: Redirect to Login
# noraml email/password login
# such users can only be added by support
@router.post("/login", 
    summary="Login with email and password",
    description="Authenticate a user with email and password credentials",
    response_description="Authentication token and user information",
    responses={
        200: {
            "description": "Successful authentication",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "user@example.com",
                            "name": "John Doe",
                            "role": "student",
                            "is_google_user": False,
                            "has_password": True
                        }
                    }
                }
            }
        },
        400: {
            "description": "Authentication failed - Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect email or password"}
                }
            }
        }
    }
)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Authenticate a user with email and password.
    
    This endpoint allows users to log in using their email and password credentials.
    It returns a JWT token that can be used for subsequent authenticated requests.
    
    Args:
        form_data: The OAuth2 form containing username (email) and password
        db: Database session
        
    Returns:
        JSON response with access token and user information
        
    Raises:
        HTTPException: If authentication fails due to invalid credentials
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    user = await authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    logger.info(f"Successful login for user: {form_data.username}, role: {user.role}")
    access_token = create_access_token(data={"email": user.email, "role": user.role, "sub": str(user.id)})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "is_google_user": user.is_google_user,
            "has_password": bool(user.hashed_password)
        }
    }

# google login
@router.get("/login/google", 
    summary="Login with Google",
    description="Initiates the Google OAuth2 authentication flow",
    response_description="Redirects to Google for authentication",
    responses={
        307: {
            "description": "Temporary redirect to Google authentication page"
        },
        500: {
            "description": "Server error during OAuth initialization",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to initialize Google OAuth"}
                }
            }
        }
    }
)
async def login_with_google(request: Request):
    """
    Initiate Google OAuth2 authentication flow.
    
    This endpoint redirects the user to Google's authentication page.
    After successful authentication with Google, the user will be redirected
    back to the callback endpoint.
    
    Args:
        request: The incoming request object
        
    Returns:
        A redirect response to Google's authentication page
    """
    logger.info("Starting Google login process")
    # Use the same redirect URI as configured in the OAuth client
    redirect_uri = "http://localhost:8000/auth/callback"
    logger.info(f"Using redirect URI: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)

# Step 2: Google Callback
@router.get("/callback", 
    summary="Google OAuth callback",
    description="Handles the callback from Google OAuth2 authentication",
    response_description="Redirects to frontend with authentication token",
    responses={
        307: {
            "description": "Temporary redirect to frontend with authentication token"
        },
        400: {
            "description": "Bad request - Invalid token or authentication failed",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        },
        500: {
            "description": "Server error during authentication",
            "content": {
                "application/json": {
                    "example": {"detail": "Authentication error"}
                }
            }
        }
    }
)
async def auth_callback(request: Request, db=Depends(get_db)):
    """
    Handle the callback from Google OAuth2 authentication.
    
    This endpoint processes the response from Google after a user has authenticated.
    It creates or retrieves the user account, generates a JWT token, and redirects
    to the frontend with the token.
    
    Args:
        request: The incoming request object with OAuth data
        db: Database session
        
    Returns:
        A redirect response to the frontend with the authentication token
        
    Raises:
        HTTPException: If authentication fails
    """
    logger.info("Processing OAuth callback")
    try:
        token = await oauth.google.authorize_access_token(request)
        logger.info(f"Received OAuth token")
        
        user_data = await oauth.google.parse_id_token(token, None)
        logger.info(f"Parsed user data: {user_data.get('email')}")
        
        # Log complete user data for debugging
        logger.info(f"Google user data: {user_data}")
        logger.info(f"Google profile picture: {user_data.get('picture')}")
        
        request.session["user"] = user_data

        # Check if user is already stored in db
        user = await get_or_create_user(db, user_data)
        logger.info(f"User retrieved/created: {user.email}, role: {user.role}")

        if not user_data:
            logger.error("Invalid token or user data")
            raise HTTPException(status_code=400, detail="Invalid token")

        # Create JWT token
        access_token = create_access_token(data={"email": user.email, "role": user.role, "sub": str(user.id)})
        logger.info(f"Created JWT token")
        
        # Check if user has a password set
        has_password = bool(user.hashed_password)
        password_notification = "" if has_password else "&password_needed=true"
        
        # Redirect to frontend with token and user role
        frontend_callback_url = f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&user_role={user.role}{password_notification}"
        logger.info(f"Redirecting to frontend callback with role: {user.role}")
        return RedirectResponse(url=frontend_callback_url)
    except Exception as e:
        logger.error(f"Error in auth callback: {str(e)}")
        # Redirect to frontend with error
        error_url = f"{settings.FRONTEND_URL}/login?error=authentication_failed"
        logger.info(f"Redirecting to error URL")
        return RedirectResponse(url=error_url)

# Step 3: Get Current User (Frontend Calls This)
@router.get("/me", 
    summary="Get current user information",
    description="Retrieves information about the currently authenticated user",
    response_description="User information from the JWT token",
    responses={
        200: {
            "description": "User information retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "email": "user@example.com",
                        "role": "student",
                        "sub": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing token",
            "content": {
                "application/json": {
                    "example": {"detail": "No authentication token provided"}
                }
            }
        }
    }
)
async def get_user(token: str = Depends(oauth2_scheme)):
    """
    Get information about the currently authenticated user.
    
    This endpoint decodes the JWT token to retrieve information about the
    currently authenticated user, including email, role, and user ID.
    
    Args:
        token: JWT authentication token
        
    Returns:
        JSON response with user information from the token
        
    Raises:
        HTTPException: If authentication fails or token is invalid
    """
    logger = logging.getLogger(__name__)
    
    # Log token for debugging
    logger.info(f"Received token in /auth/me: {token[:10] if token else 'None'}...")
    
    if not token:
        logger.error("No token provided")
        raise HTTPException(
            status_code=401, 
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not is_token_valid(token):
        logger.error("Token validation failed")
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if not payload:
        logger.error("Token decoding failed")
        raise HTTPException(
            status_code=401, 
            detail="Failed to decode token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Successfully decoded token payload: {payload}")
    return payload

# Step 4: Logout
@router.get("/logout", 
    summary="Logout user",
    description="Invalidates the current authentication token",
    response_description="Confirmation of successful logout",
    responses={
        200: {
            "description": "Successfully logged out",
            "content": {
                "application/json": {
                    "example": {"message": "Logged out successfully"}
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing token",
            "content": {
                "application/json": {
                    "example": {"detail": "No authentication token provided"}
                }
            }
        },
        500: {
            "description": "Server error during logout",
            "content": {
                "application/json": {
                    "example": {"detail": "Error during logout"}
                }
            }
        }
    }
)
async def logout(token: str = Depends(oauth2_scheme)):
    """
    Logout the current user by invalidating their authentication token.
    
    This endpoint blacklists the current JWT token, effectively logging out the user.
    Once a token is blacklisted, it can no longer be used for authentication.
    
    Args:
        token: JWT authentication token
        
    Returns:
        JSON response confirming successful logout
        
    Raises:
        HTTPException: If authentication fails or token blacklisting fails
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Logout request received with token: {token[:10] if token else 'None'}...")
    
    if not token:
        logger.error("No token provided for logout")
        raise HTTPException(
            status_code=401, 
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if is_token_valid(token):
        try:
            redis_client.set(f'blacklist:{token}', "")
            logger.info(f"Token blacklisted successfully: {token[:10]}...")
            return {"message": "Logged out successfully"}
        except Exception as e:
            logger.error(f"Error blacklisting token: {str(e)}")
            raise HTTPException(status_code=500, detail="Error during logout")
    else:
        logger.warning(f"Invalid token provided for logout: {token[:10]}...")
        return {"message": "Invalid token, no action taken"}

# Step 5: Refresh Token
@router.post("/refresh", 
    summary="Refresh authentication token",
    description="Issues a new JWT token to extend the user's session",
    response_description="New authentication token",
    responses={
        200: {
            "description": "Token refreshed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        },
        500: {
            "description": "Server error during token refresh",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            }
        }
    }
)
async def refresh_token(token: str = Depends(oauth2_scheme)):
    """
    Refresh the user's authentication token.
    
    This endpoint issues a new JWT token to extend the user's session.
    The current token is blacklisted to prevent reuse.
    
    Args:
        token: Current JWT authentication token
        
    Returns:
        JSON response with a new access token
        
    Raises:
        HTTPException: If authentication fails or token refresh fails
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Refresh token request received with token: {token[:10] if token else 'None'}...")
    
    if not token:
        logger.error("No token provided for refresh")
        raise HTTPException(
            status_code=401, 
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify the token is valid
        if not is_token_valid(token):
            logger.warning(f"Invalid token provided for refresh: {token[:10]}...")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Decode the token to get the user_id
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            logger.error("Token does not contain user ID")
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        logger.info(f"Refreshing token for user ID: {user_id}")
        
        # Blacklist the old token
        try:
            redis_client.set(f'blacklist:{token}', "")
            logger.info(f"Old token blacklisted successfully: {token[:10]}...")
        except Exception as e:
            logger.error(f"Error blacklisting old token: {str(e)}")
            # Continue with refresh even if blacklisting fails
        
        # Create a new token
        access_token = create_access_token(data={"sub": user_id})
        logger.info(f"New token created successfully for user ID: {user_id}")
        
        return {"access_token": access_token, "token_type": "bearer"}
    except jwt.JWTError as e:
        logger.error(f"JWT error during token refresh: {str(e)}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not logged in")
    return user

# Role based access control
def require_role(role: str):
    async def role_checker(token: str = Depends(oauth2_scheme)):
        user = await get_current_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        if user["role"] != role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker

# Example usage:
# @router.get("/protected")
# async def protected_route(user: dict = Depends(require_role("admin"))):
#     return {"message": "You have access!"}

# roles list : student, faculty, support

class PasswordUpdate(BaseModel):
    """
    Schema for password update requests.
    
    Attributes:
        password: The new password to set for the user
    """
    password: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "password": "securePassword123"
            }
        }
    )

@router.post("/set-password", 
    summary="Set or update user password",
    description="Allows users to set a password for their account, particularly useful for users who initially logged in with Google",
    response_description="Confirmation message upon successful password update",
    responses={
        200: {
            "description": "Password successfully set",
            "content": {
                "application/json": {
                    "example": {"message": "Password set successfully"}
                }
            }
        },
        400: {
            "description": "Bad request - Invalid password or failed to set password",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to set password"}
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing token",
            "content": {
                "application/json": {
                    "example": {"detail": "Authentication required"}
                }
            }
        }
    }
)
async def set_password(
    password_data: PasswordUpdate, 
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Set or update a password for the authenticated user.
    
    This endpoint allows users who initially logged in with Google to set a password,
    enabling them to subsequently log in using email/password authentication.
    
    Args:
        password_data: The new password data
        token: JWT authentication token
        db: Database session
        
    Returns:
        JSON response with success message
        
    Raises:
        HTTPException: If authentication fails or password update fails
    """
    logger.info("Password update request received")
    
    if not token:
        logger.error("No token provided for password update")
        raise HTTPException(
            status_code=401, 
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not is_token_valid(token):
        logger.error("Invalid token for password update")
        raise HTTPException(
            status_code=401, 
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decode token to get user ID
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        logger.error("Token does not contain user ID")
        raise HTTPException(status_code=400, detail="Invalid token payload")
    
    user_id = payload["sub"]
    logger.info(f"Setting password for user ID: {user_id}")
    
    # Set the password
    success = await set_user_password(db, user_id, password_data.password)
    
    if not success:
        logger.error(f"Failed to set password for user ID: {user_id}")
        raise HTTPException(status_code=400, detail="Failed to set password")
    
    logger.info(f"Password successfully set for user ID: {user_id}")
    return {"message": "Password set successfully"}