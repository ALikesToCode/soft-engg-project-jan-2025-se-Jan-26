from app.services.auth_service import get_or_create_user
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request
from ..config import settings

router = APIRouter()

# Initialize OAuth
config = Config(".env")
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params={"scope": "openid email profile"},
    access_token_url="https://oauth2.googleapis.com/token",
    access_token_params=None,
    userinfo_url="https://www.googleapis.com/oauth2/v3/userinfo",
    client_kwargs={"scope": "openid email profile"},
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
)

# Step 1: Redirect to Google Login
@router.get("/auth/login")
async def login_with_google(request: Request):
    redirect_uri = request.url_for("auth_callback")  # Google will redirect here
    return await oauth.google.authorize_redirect(request, redirect_uri)

# Step 2: Google Callback
@router.get("/auth/callback")
async def auth_callback(request: Request, db=Depends(get_db)): # -> dict :
    token = await oauth.google.authorize_access_token(request)
    user_data = await oauth.google.parse_id_token(token, None)
    request.session["user"] = user_data

    # Check if user is already stored in db
    user = await get_or_create_user(db, user_data)

    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid token")

    return {"message": "Authenticated", "user": user_data}

# Step 3: Get Current User (Frontend Calls This)
@router.get("/auth/me")
async def get_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not logged in")
    return user