from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, desc
import uuid

from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQUpdate


async def get_faqs(db: AsyncSession, category_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[FAQ]:
    """
    Get all FAQs, optionally filtered by category.
    
    Args:
        db: Database session
        category_id: Optional category ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of FAQ objects
    """
    query = select(FAQ).order_by(desc(FAQ.priority), FAQ.created_at)
    
    if category_id and category_id != "all":
        query = query.filter(FAQ.category_id == category_id)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def get_faq(db: AsyncSession, faq_id: uuid.UUID) -> Optional[FAQ]:
    """
    Get a specific FAQ by ID.
    
    Args:
        db: Database session
        faq_id: UUID of the FAQ to retrieve
        
    Returns:
        FAQ object if found, None otherwise
    """
    result = await db.execute(select(FAQ).filter(FAQ.id == faq_id))
    return result.scalars().first()


async def create_faq(db: AsyncSession, faq: FAQCreate) -> FAQ:
    """
    Create a new FAQ.
    
    Args:
        db: Database session
        faq: FAQ data
        
    Returns:
        Created FAQ object
    """
    db_faq = FAQ(**faq.model_dump())
    db.add(db_faq)
    await db.commit()
    await db.refresh(db_faq)
    return db_faq


async def update_faq(db: AsyncSession, faq_id: uuid.UUID, faq: FAQUpdate) -> Optional[FAQ]:
    """
    Update an existing FAQ.
    
    Args:
        db: Database session
        faq_id: UUID of the FAQ to update
        faq: Updated FAQ data
        
    Returns:
        Updated FAQ object if found, None otherwise
    """
    db_faq = await get_faq(db, faq_id)
    if not db_faq:
        return None
    
    update_data = faq.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_faq, key, value)
    
    await db.commit()
    await db.refresh(db_faq)
    return db_faq


async def delete_faq(db: AsyncSession, faq_id: uuid.UUID) -> bool:
    """
    Delete an FAQ.
    
    Args:
        db: Database session
        faq_id: UUID of the FAQ to delete
        
    Returns:
        True if FAQ was deleted, False otherwise
    """
    db_faq = await get_faq(db, faq_id)
    if not db_faq:
        return False
    
    await db.delete(db_faq)
    await db.commit()
    return True


async def search_faqs(db: AsyncSession, query: str, limit: int = 20) -> List[FAQ]:
    """
    Search FAQs by query string.
    
    Args:
        db: Database session
        query: Search query string
        limit: Maximum number of records to return
        
    Returns:
        List of matching FAQ objects
    """
    search_query = f"%{query.lower()}%"
    result = await db.execute(
        select(FAQ)
        .filter(
            or_(
                FAQ.question.ilike(search_query),
                FAQ.answer.ilike(search_query)
            )
        )
        .order_by(desc(FAQ.priority), FAQ.created_at)
        .limit(limit)
    )
    return result.scalars().all() 