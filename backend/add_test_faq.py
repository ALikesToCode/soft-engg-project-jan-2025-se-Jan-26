import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models.faq import FAQ

async def add_test_faq():
    """Add a test FAQ to the database."""
    async with async_session() as session:
        # Create a test FAQ
        test_faq = FAQ(
            question="What is the deadline for assignment submission?",
            answer="The deadline for assignment submission is typically mentioned in the assignment details. Please check the assignment page for specific deadlines.",
            category_id="general",
            priority=10
        )
        
        # Add to session and commit
        session.add(test_faq)
        await session.commit()
        
        print(f"Added test FAQ with ID: {test_faq.id}")

if __name__ == "__main__":
    asyncio.run(add_test_faq()) 