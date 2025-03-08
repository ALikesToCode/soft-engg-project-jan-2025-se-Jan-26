import jwt
from datetime import datetime, timedelta, UTC
from app.config import settings
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# SECRET_KEY = "your_secret_key"  # Replace with your actual secret key
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode["exp"] = expire
        
        # Log token creation details
        user_id = to_encode.get("sub", "unknown")
        logger.info(f"Creating token for user ID: {user_id} with expiry: {expire}")
        logger.debug(f"Token payload: {to_encode}")
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        # Log only the first 10 characters of the token for security
        logger.info(f"Token created successfully: {encoded_jwt[:10]}...")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise e

def decode_access_token(token: str):
    try:
        # Remove 'Bearer ' prefix if present
        if token and token.startswith('Bearer '):
            token = token[7:]
            logger.debug("Removed 'Bearer ' prefix from token")
        
        if not token:
            logger.error("Empty token provided for decoding")
            return None
            
        logger.info(f"Attempting to decode token: {token[:10]}...")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Log successful decoding
        user_id = payload.get("sub", "unknown")
        expiry = datetime.fromtimestamp(payload.get("exp", 0))
        logger.info(f"Token decoded successfully for user ID: {user_id}, expires: {expiry}")
        logger.debug(f"Full decoded payload: {payload}")
        
        return payload
    except jwt.ExpiredSignatureError:
        logger.error(f"Token expired: {token[:10]}...")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {token[:10]}... Error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {token[:10]}... Error: {str(e)}")
        return None
    
# # testing encoding and decodeing
# data = {"email": "abc@gmail.com", "role": "admin"}
# token = create_access_token(data)
# print(token)
# payload = decode_access_token(token)
# print(payload)