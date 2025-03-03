import asyncio
from app.database import get_db, Base, engine
from app.models.user import User
from sqlalchemy.future import select
import uuid
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def create_test_user():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async for db in get_db():
        user = await db.execute(select(User).where(User.email == 'test@example.com'))
        user = user.scalars().first()
        
        if not user:
            user = User(
                id=uuid.uuid4(),
                email='test@example.com',
                name='Test User',
                role='faculty',
                hashed_password=pwd_context.hash('test123'),
                created_at=datetime.now()
            )
            db.add(user)
            await db.commit()
            print(f'Created user: {user.email} with role: {user.role} and id: {user.id}')
        else:
            print(f'User already exists: {user.email} with role: {user.role} and id: {user.id}')
        break  # Exit after first iteration

if __name__ == "__main__":
    asyncio.run(create_test_user()) 