from fastapi import APIRouter, HTTPException, status
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health", 
    summary="Health check endpoint",
    description="Check if the API is up and running",
    response_description="API health status"
)
async def health_check():
    """
    Get health status of the API
    
    Returns:
        Health status information
    """
    try:
        return {
            "status": "ok",
            "message": "API is running"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        ) 