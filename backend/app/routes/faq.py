from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user, get_current_admin_user
from app.services import faq_service
from app.schemas.faq import FAQCreate, FAQUpdate, FAQResponse, FAQRating, FAQSearchQuery

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/faqs",
    tags=["FAQs"],
    responses={404: {"description": "Not found"}},
)

# Custom dependency to check for admin or support role
async def get_faq_editor(current_user: dict = Depends(get_current_user)):
    """
    Verify the current user has rights to edit FAQs (admin or support role).
    """
    if current_user.get("role") not in ["admin", "support"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or support role required"
        )
    return current_user

@router.get("/", response_model=List[FAQResponse])
async def read_faqs(
    category_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all FAQs with optional filtering by category.
    This endpoint is public and does not require authentication.
    """
    return await faq_service.get_faqs(db, category_id, skip, limit)


@router.post("/", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(
    faq: FAQCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_faq_editor)
):
    """
    Create a new FAQ (admin or support role required).
    """
    return await faq_service.create_faq(db, faq)


@router.get("/{faq_id}", response_model=FAQResponse)
async def read_faq(
    faq_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific FAQ by ID.
    This endpoint is public and does not require authentication.
    """
    faq = await faq_service.get_faq(db, faq_id)
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found"
        )
    return faq


@router.put("/{faq_id}", response_model=FAQResponse)
async def update_faq(
    faq_id: UUID,
    faq_update: FAQUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_faq_editor)
):
    """
    Update a FAQ (admin or support role required).
    """
    updated_faq = await faq_service.update_faq(db, faq_id, faq_update)
    if not updated_faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found"
        )
    return updated_faq


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    faq_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_faq_editor)
):
    """
    Delete a FAQ (admin or support role required).
    """
    deleted = await faq_service.delete_faq(db, faq_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found"
        )


@router.post("/search", response_model=List[FAQResponse])
async def search_for_faqs(
    query: FAQSearchQuery,
    db: AsyncSession = Depends(get_db)
):
    """
    Search for FAQs based on a query string.
    This endpoint is public and does not require authentication.
    
    This endpoint uses a combination of vector search (for semantic matching)
    and keyword search to find the most relevant FAQs.
    """
    return await faq_service.search_faqs(db, query.query, query.limit)


@router.post("/vector-search", response_model=List[FAQResponse])
async def vector_search_faqs(
    query: FAQSearchQuery,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Search for FAQs using vector search only (semantic search).
    
    This endpoint uses vector embeddings to find semantically similar FAQs,
    which can find relevant results even when keywords don't match exactly.
    """
    results = await faq_service.vector_search_faqs(query.query, query.limit)
    if not results:
        # Fall back to regular search if vector search returns no results
        logger.info(f"Vector search returned no results, falling back to keyword search")
        results = await faq_service.search_faqs(db, query.query, query.limit)
    return results


@router.post("/initialize-vector-store", status_code=status.HTTP_202_ACCEPTED)
async def initialize_faq_vector_store(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_faq_editor)
):
    """
    Initialize or rebuild the FAQ vector store (admin or support role required).
    
    This endpoint will add all existing FAQs to the vector store for semantic search.
    This is a potentially long-running operation, so it runs in the background.
    """
    # Start the initialization in the background
    async def init_vector_store():
        try:
            # Get all FAQs
            faqs = await faq_service.get_faqs(db)
            logger.info(f"Initializing vector store with {len(faqs)} FAQs")
            
            # Add each FAQ to the vector store
            success_count = 0
            for faq in faqs:
                if await faq_service.add_faq_to_vector_store(faq):
                    success_count += 1
            
            logger.info(f"Successfully added {success_count} of {len(faqs)} FAQs to vector store")
        except Exception as e:
            logger.error(f"Error initializing FAQ vector store: {str(e)}")
    
    # Schedule the background task
    background_tasks.add_task(init_vector_store)
    
    return {"message": "Vector store initialization started in the background"}


@router.post("/{faq_id}/rate", status_code=status.HTTP_200_OK)
async def rate_faq(
    faq_id: UUID,
    rating: FAQRating,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Rate an FAQ as helpful or not.
    """
    # In a real implementation, we would store the rating
    # For now, we'll just return a success message
    return {"message": "Rating submitted successfully"} 