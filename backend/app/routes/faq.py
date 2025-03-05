from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services import faq_service
from app.schemas.faq import FAQCreate, FAQUpdate, FAQResponse, FAQRating, FAQSearchQuery

router = APIRouter(
    prefix="/api/v1/faqs",
    tags=["FAQs"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[FAQResponse])
async def read_faqs(
    category_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve all FAQs with optional filtering by category.
    """
    return await faq_service.get_faqs(db, category_id, skip, limit)


@router.get("/{faq_id}", response_model=FAQResponse)
async def read_faq(
    faq_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve a specific FAQ by its ID.
    """
    faq = await faq_service.get_faq(db, faq_id)
    if faq is None:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq


@router.post("/", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_new_faq(
    faq: FAQCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new FAQ.
    """
    return await faq_service.create_faq(db, faq)


@router.put("/{faq_id}", response_model=FAQResponse)
async def update_existing_faq(
    faq_id: UUID,
    faq_update: FAQUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update an existing FAQ (requires support role).
    """
    if current_user.get("role") != "support":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update FAQs"
        )
    
    updated_faq = await faq_service.update_faq(db, faq_id, faq_update)
    if not updated_faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    return updated_faq


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_faq(
    faq_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete an FAQ (requires support role).
    """
    if current_user.get("role") != "support":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete FAQs"
        )
    
    deleted = await faq_service.delete_faq(db, faq_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="FAQ not found")


@router.post("/search", response_model=List[FAQResponse])
async def search_for_faqs(
    query: FAQSearchQuery,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Search for FAQs based on a query string.
    """
    return await faq_service.search_faqs(db, query.query, query.limit)


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