import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models.faq import FAQ
from sqlalchemy.future import select

async def check_faqs():
    """Check if there are any FAQs in the database."""
    async with async_session() as session:
        result = await session.execute(select(FAQ))
        faqs = result.scalars().all()
        
        print(f"Found {len(faqs)} FAQs in the database:")
        for faq in faqs:
            print(f"ID: {faq.id}")
            print(f"Question: {faq.question}")
            print(f"Answer: {faq.answer}")
            print(f"Category: {faq.category_id}")
            print(f"Priority: {faq.priority}")
            print(f"Created at: {faq.created_at}")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(check_faqs()) 