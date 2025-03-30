from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, desc
import uuid
import logging

from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQUpdate

# Setup logging
logger = logging.getLogger(__name__)

# Mock vector store implementation
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
        query = query.filter(FAQ.category_id == str(category_id))
    
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


async def create_faq(db: AsyncSession, faq_create: FAQCreate) -> FAQ:
    """
    Create a new FAQ.
    
    Args:
        db: Database session
        faq_create: FAQ data
        
    Returns:
        Created FAQ object
    """
    faq = FAQ(
        id=uuid.uuid4(),
        question=faq_create.question,
        answer=faq_create.answer,
        category_id=faq_create.category_id,
        priority=faq_create.priority
    )
    
    db.add(faq)
    await db.commit()
    await db.refresh(faq)
    
    # Mock: Add to vector store - log but don't actually do it
    logger.info(f"Mock: Added FAQ {faq.id} to vector store")
    
    return faq


async def update_faq(db: AsyncSession, faq_id: str, faq_update: FAQUpdate) -> Optional[FAQ]:
    """
    Update an existing FAQ.
    
    Args:
        db: Database session
        faq_id: ID of the FAQ to update
        faq_update: Updated FAQ data
        
    Returns:
        Updated FAQ object or None if not found
    """
    result = await db.execute(select(FAQ).filter(FAQ.id == str(faq_id)))
    faq = result.scalars().first()
    
    if not faq:
        return None
    
    for key, value in faq_update.dict(exclude_unset=True).items():
        setattr(faq, key, value)
    
    await db.commit()
    await db.refresh(faq)
    
    # Mock: Update in vector store - log but don't actually do it
    logger.info(f"Mock: Updated FAQ {faq.id} in vector store")
    
    return faq


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
    Search FAQs by query string using both keyword search and vector search.
    
    Args:
        db: Database session
        query: Search query string
        limit: Maximum number of records to return
        
    Returns:
        List of matching FAQ objects
    """
    # Skip mock vector search and use only keyword search
    logger.info(f"Using keyword search for query: {query}")
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


async def vector_search_faqs(query: str, limit: int = 20) -> List[FAQ]:
    """
    Search FAQs using vector embeddings for semantic search.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List of matching FAQ objects
    """
    # Mock implementation - return empty list
    logger.info(f"Mock vector search for: {query} (returning empty list)")
    return []


async def add_faq_to_vector_store(faq: FAQ) -> bool:
    """
    Add or update an FAQ in the vector store.
    
    Args:
        faq: FAQ object to add to vector store
        
    Returns:
        True if successful, False otherwise
    """
    # Mock implementation - just return success
    logger.info(f"Mock: Added FAQ {faq.id} to vector store")
    return True 