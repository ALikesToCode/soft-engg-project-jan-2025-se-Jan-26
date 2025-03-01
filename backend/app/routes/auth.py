from app.services.auth_service import authenticate_user, get_or_create_user, get_current_user, oauth2_scheme
from app.database import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.jwt_utils import create_access_token, decode_access_token
from fastapi import APIRouter, Depends, HTTPException
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request
import redis
from ..config import settings
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)  # Store in Redis

def is_token_blacklisted(token: str):
    return redis_client.exists(f'blacklist:{token}')

def is_token_valid(token: str):
    payload = decode_access_token(token)
    if not payload:
        return False
    return not is_token_blacklisted(token)

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
    redirect_uri = request.url_for("auth_callback")  # Google will redirect here
    return await oauth.google.authorize_redirect(request, redirect_uri)

# Step 2: Google Callback
@router.get("/auth/callback")
async def auth_callback(request: Request, db=Depends(get_db)) -> dict :
    token = await oauth.google.authorize_access_token(request)
    user_data = await oauth.google.parse_id_token(token, None)
    request.session["user"] = user_data

    # Check if user is already stored in db
    user = await get_or_create_user(db, user_data)

    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid token")

    access_token = create_access_token(data={"email": user.email, "role": user.role})
    return {"message": "Authenticated", "access_token": access_token, "user-data": user_data}

# Step 3: Get Current User (Frontend Calls This)
@router.get("/auth/me")
async def get_user(token: str = Depends(oauth2_scheme)):
    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

# Step 4: Logout
@router.get("/auth/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    if is_token_valid(token):
        redis_client.set(f'blacklist:{token}', "")
        return {"message": "Logged out"}
    return {"message": "Invalid token"}

# Step 5: Refresh Token
@router.get("/auth/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    access_token = create_access_token(data={"email": payload["email"], "role": payload["role"]})
    return {"access_token": access_token, "token_type": "bearer"}

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