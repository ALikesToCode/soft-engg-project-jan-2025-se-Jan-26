from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Optional, List, Dict, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.routes.auth import get_current_user
from app.services.course_service import get_modules_by_course
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request validation
class RoadmapProgressUpdate(BaseModel):
    roadmapId: str
    milestoneId: int
    status: str

@router.get("/generate/{course_id}", 
    summary="Generate a learning roadmap for a course",
    description="Creates a personalized learning roadmap based on course modules",
    response_description="A structured learning roadmap with milestones and materials"
)
async def generate_roadmap(
    course_id: str,
    difficulty_level: Optional[str] = "intermediate",
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a learning roadmap for a specific course.
    
    This endpoint analyzes the course structure and creates a personalized
    learning roadmap with milestones and learning materials.
    
    Args:
        course_id: The ID of the course to generate a roadmap for
        difficulty_level: The preferred difficulty level (beginner, intermediate, advanced)
        current_user: The authenticated user
        db: Database session
        
    Returns:
        A structured roadmap object
    """
    try:
        logger.info(f"Generating roadmap for course {course_id} with difficulty {difficulty_level}")
        
        # Get course modules
        try:
            # Use current user's ID for authorization
            user_id = current_user.get("id")
            modules = await get_modules_by_course(course_id, db, user_id)
        except Exception as e:
            logger.error(f"Error fetching course modules: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error fetching course modules: {str(e)}"
            )
        
        # Structure for a learning roadmap
        roadmap = {
            "id": uuid.uuid4().hex,
            "title": f"Learning Path for Course {course_id}",
            "description": f"Personalized roadmap with {difficulty_level} difficulty",
            "completedSteps": 0,
            "totalSteps": len(modules),
            "milestones": []
        }
        
        # Create milestones from modules
        position = 0
        for module in modules:
            position += 1
            milestone = {
                "id": position,
                "title": module.get("title", f"Module {position}"),
                "description": module.get("description", "No description available"),
                "status": "locked" if position > 1 else "in_progress",
                "estimatedTime": f"{position} week{'s' if position > 1 else ''}",
                "locked": position > 1,
                "materials": []
            }
            
            # Add materials based on module content
            material_id = 1
            for _ in range(min(2, position)):  # Add 1-2 materials per milestone
                material_type = ["video", "exercise", "project", "tutorial", "course"][material_id % 5]
                milestone["materials"].append({
                    "id": material_id,
                    "type": material_type,
                    "title": f"{module.get('title', 'Module')} - Material {material_id}",
                    "description": f"Learning material for {module.get('title', 'this module')}",
                    "duration": f"{material_id + 1} hours",
                    "url": f"/course/{course_id}/module/{module.get('id', 0)}/material/{material_id}"
                })
                material_id += 1
            
            roadmap["milestones"].append(milestone)
        
        return {"roadmap": roadmap}
        
    except Exception as e:
        logger.error(f"Error generating roadmap: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating roadmap: {str(e)}"
        )

@router.post("/progress", 
    summary="Update progress in a learning roadmap",
    description="Updates the completion status of a milestone in a learning roadmap",
    response_description="Updated progress information"
)
async def update_roadmap_progress(
    progress: RoadmapProgressUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user's progress in a learning roadmap.
    
    This endpoint allows marking milestones as completed, in-progress, etc.
    
    Args:
        progress: The progress update information
        current_user: The authenticated user
        db: Database session
        
    Returns:
        Updated progress information
    """
    try:
        logger.info(f"Updating roadmap progress for user {current_user.get('id')}, "
                   f"roadmap {progress.roadmapId}, milestone {progress.milestoneId}")
        
        # In a production app, we would save this to a database
        # For now, we'll just return success
        
        # Mock: Fetch current user's roadmap progress
        # In a real app, this would come from the database
        
        # Mock response
        return {
            "success": True,
            "userId": current_user.get("id"),
            "roadmapId": progress.roadmapId,
            "milestoneId": progress.milestoneId,
            "status": progress.status,
            "updatedAt": str(uuid.uuid4())  # Mock timestamp
        }
        
    except Exception as e:
        logger.error(f"Error updating roadmap progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating roadmap progress: {str(e)}"
        ) 