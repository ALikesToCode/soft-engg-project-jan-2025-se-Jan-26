from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db
from app.services.auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["modules"],
    responses={404: {"description": "Not found"}}
)

@router.get("/{module_id}", 
    summary="Get module details",
    description="Retrieves details for a specific module",
    response_description="Module details including all content and materials"
)
async def get_module(
    module_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get details for a specific module.
    
    This endpoint retrieves comprehensive information about a module, including
    all content sections, materials, and supplementary resources.
    
    Args:
        module_id: The ID of the module to retrieve
        current_user: The authenticated user
        db: Database session
        
    Returns:
        Module details
    """
    try:
        # This is a placeholder implementation
        # In a real implementation, we would fetch from the database
        logger.info(f"Getting details for module {module_id}")
        
        # Mock response
        return {
            "id": module_id,
            "title": f"Module {module_id}",
            "description": "Module description placeholder",
            "course_id": "course-123",
            "order": 1,
            "status": "published",
            "content_sections": [
                {
                    "id": "section-1",
                    "title": "Introduction",
                    "content": "Welcome to this module",
                    "order": 1
                }
            ],
            "materials": [
                {
                    "id": "material-1",
                    "title": "Module Slides",
                    "type": "pdf",
                    "url": f"/api/modules/{module_id}/materials/slides.pdf"
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving module {module_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving module: {str(e)}"
        )

@router.get("/{module_id}/materials", 
    summary="Get module materials",
    description="Retrieves all materials for a specific module",
    response_description="List of module materials"
)
async def get_module_materials(
    module_id: str,
    material_type: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get materials for a specific module.
    
    This endpoint retrieves all learning materials associated with a module,
    with optional filtering by material type.
    
    Args:
        module_id: The ID of the module
        material_type: Optional filter for material type (e.g., "pdf", "video", "assignment")
        current_user: The authenticated user
        db: Database session
        
    Returns:
        List of module materials
    """
    try:
        # This is a placeholder implementation
        logger.info(f"Getting materials for module {module_id}, type filter: {material_type}")
        
        # Mock response
        materials = [
            {
                "id": "material-1",
                "title": "Module Slides",
                "type": "pdf",
                "description": "Presentation slides for the module",
                "url": f"/api/modules/{module_id}/materials/slides.pdf",
                "created_at": "2023-01-01T00:00:00Z",
                "order": 1
            },
            {
                "id": "material-2",
                "title": "Lecture Recording",
                "type": "video",
                "description": "Video recording of the lecture",
                "url": f"/api/modules/{module_id}/materials/lecture.mp4",
                "created_at": "2023-01-01T00:00:00Z",
                "order": 2
            }
        ]
        
        # Apply filter if provided
        if material_type:
            materials = [m for m in materials if m["type"] == material_type]
            
        return {"materials": materials}
        
    except Exception as e:
        logger.error(f"Error retrieving materials for module {module_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving module materials: {str(e)}"
        ) 