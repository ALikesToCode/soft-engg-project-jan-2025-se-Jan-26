from typing import Dict, Any, List
from fastapi.openapi.utils import get_openapi as fastapi_get_openapi
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)

def get_openapi(
    title: str,
    version: str,
    description: str,
    routes: List[Any],
    *,
    openapi_version: str = "3.0.2",
) -> Dict[str, Any]:
    """
    Generate an OpenAPI schema from FastAPI routes.
    
    This is a wrapper around FastAPI's get_openapi that works 
    with a list of routes instead of needing the full app instance.
    
    Args:
        title: API title
        version: API version
        description: API description
        routes: List of routes to include
        openapi_version: OpenAPI schema version
        
    Returns:
        OpenAPI schema as a dictionary
    """
    try:
        # Create a temporary FastAPI app with the routes
        app = FastAPI()
        for route in routes:
            app.routes.append(route)
        
        # Generate the OpenAPI schema
        openapi_schema = fastapi_get_openapi(
            title=title,
            version=version,
            description=description,
            routes=app.routes,
            openapi_version=openapi_version,
        )
        
        return openapi_schema
    except Exception as e:
        logger.error(f"Error generating OpenAPI schema: {str(e)}")
        # Return minimal schema as fallback
        return {
            "openapi": openapi_version,
            "info": {
                "title": title,
                "version": version,
                "description": description,
            },
            "paths": {},
        } 