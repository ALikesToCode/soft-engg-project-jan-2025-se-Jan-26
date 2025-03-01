from app.services.auth_service import authenticate_user, get_or_create_user, get_current_user, oauth2_scheme
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

router = APIRouter()
logger = logging.getLogger(__name__)

# Use settings for Redis configuration if available, otherwise use defaults
redis_host = getattr(settings, 'REDIS_HOST', '127.0.0.1')
redis_port = getattr(settings, 'REDIS_PORT', 6379)
redis_db = getattr(settings, 'REDIS_DB', 0)

# Initialize Redis client with error handling
try:
    redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
    # Test connection
    redis_client.ping()
    logger.info("Redis connection established successfully")
except redis.ConnectionError as e:
    logger.warning(f"Redis connection failed: {str(e)}. Using fallback mode.")
    # Create a mock Redis client for fallback
    class MockRedis:
        def __init__(self):
            self.blacklist = set()
            logger.info("Using in-memory blacklist as Redis fallback")
            
        def exists(self, key):
            return key in self.blacklist
            
        def set(self, key, value):
            self.blacklist.add(key)
            return True
            
        def ping(self):
            return True
    
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
        # If Redis is down, assume token is not blacklisted
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
    redirect_uri=f"http://localhost:8000{settings.API_PREFIX}/auth/callback",
    userinfo_url="https://www.googleapis.com/oauth2/v3/userinfo",
    client_kwargs={"scope": "openid email profile"},
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
)

# Step 1: Redirect to Login
# noraml email/password login
# such users can only be added by support
@router.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"email": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

# google login
@router.get("/auth/login/google")
async def login_with_google(request: Request):
    logger.info("Starting Google login process")
    # Use the same redirect URI as configured in the OAuth client
    redirect_uri = f"http://localhost:8000{settings.API_PREFIX}/auth/callback"
    logger.info(f"Using redirect URI: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)

# Step 2: Google Callback
@router.get("/auth/callback")
async def auth_callback(request: Request, db=Depends(get_db)):
    logger = logging.getLogger(__name__)
    logger.info("Processing OAuth callback")
    try:
        token = await oauth.google.authorize_access_token(request)
        logger.info(f"Received OAuth token")
        
        user_data = await oauth.google.parse_id_token(token, None)
        logger.info(f"Parsed user data: {user_data.get('email')}")
        
        request.session["user"] = user_data

        # Check if user is already stored in db
        user = await get_or_create_user(db, user_data)
        logger.info(f"User retrieved/created: {user.email}")

        if not user_data:
            logger.error("Invalid token or user data")
            raise HTTPException(status_code=400, detail="Invalid token")

        # Create JWT token
        access_token = create_access_token(data={"email": user.email, "role": user.role})
        logger.info(f"Created JWT token")
        
        # Redirect to frontend with token
        frontend_callback_url = f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}"
        logger.info(f"Redirecting to frontend callback")
        return RedirectResponse(url=frontend_callback_url)
    except Exception as e:
        logger.error(f"Error in auth callback: {str(e)}")
        # Redirect to frontend with error
        error_url = f"{settings.FRONTEND_URL}/login?error=authentication_failed"
        logger.info(f"Redirecting to error URL")
        return RedirectResponse(url=error_url)

# Step 3: Get Current User (Frontend Calls This)
@router.get("/auth/me")
async def get_user(token: str = Depends(oauth2_scheme)):
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
@router.get("/auth/logout")
async def logout(token: str = Depends(oauth2_scheme)):
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
@router.post("/auth/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
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
    def role_checker(token: str = Depends(oauth2_scheme)):
        user = get_current_user(token)
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