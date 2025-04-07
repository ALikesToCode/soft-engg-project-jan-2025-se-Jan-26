from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Tuple, List, Any, TypeVar, Generic
from sqlalchemy.sql import Select

T = TypeVar('T')

async def paginate_results(
    db: AsyncSession, 
    query: Select, 
    page: int = 1, 
    per_page: int = 10
) -> Tuple[int, List[Any]]:
    """
    Paginate database query results
    
    Args:
        db: Database session
        query: SQLAlchemy select query
        page: Page number (1-indexed)
        per_page: Number of items per page
        
    Returns:
        Tuple containing:
            - Total count of items
            - List of items for the requested page
    """
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Get paginated results
    paginated_query = query.limit(per_page).offset(offset)
    result = await db.execute(paginated_query)
    items = result.scalars().all()
    
    return total, items 