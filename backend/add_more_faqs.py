import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models.faq import FAQ

async def add_more_faqs():
    """Add multiple FAQs with different categories to the database."""
    async with async_session() as session:
        # Create FAQs with different categories
        faqs = [
            FAQ(
                question="How do I reset my password?",
                answer="You can reset your password by clicking on the 'Forgot Password' link on the login page and following the instructions sent to your email.",
                category_id="account",
                priority=8
            ),
            FAQ(
                question="How do I contact a faculty member?",
                answer="You can contact faculty members through the messaging system on the platform or by using their official email addresses listed in the faculty directory.",
                category_id="faculty",
                priority=7
            ),
            FAQ(
                question="What are the technical requirements for online exams?",
                answer="For online exams, you need a stable internet connection, a computer with a webcam and microphone, and the latest version of Chrome or Firefox browser.",
                category_id="technical",
                priority=9
            ),
            FAQ(
                question="How do I enroll in a course?",
                answer="You can enroll in courses through the course catalog. Navigate to the desired course and click the 'Enroll' button. Some courses may require approval from the course instructor.",
                category_id="courses",
                priority=10
            )
        ]
        
        # Add to session and commit
        for faq in faqs:
            session.add(faq)
        
        await session.commit()
        
        print(f"Added {len(faqs)} new FAQs to the database")

if __name__ == "__main__":
    asyncio.run(add_more_faqs()) 