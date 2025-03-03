import asyncio
from app.database import get_db, Base, engine
from app.models.user import User
from sqlalchemy.future import select
import uuid
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def create_test_users():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    test_users = [
        {
            'email': 'student@study.iitm.ac.in',
            'name': 'Test Student',
            'role': 'student',
            'password': 'student'
        },
        {
            'email': 'faculty@study.iitm.ac.in',
            'name': 'Test Faculty',
            'role': 'faculty',
            'password': 'faculty'
        },
        {
            'email': 'support@study.iitm.ac.in',
            'name': 'Test Support',
            'role': 'support',
            'password': 'support'
        }
    ]
    
    async for db in get_db():
        for user_data in test_users:
            user = await db.execute(select(User).where(User.email == user_data['email']))
            user = user.scalars().first()
            
            if not user:
                user = User(
                    id=uuid.uuid4(),
                    email=user_data['email'],
                    name=user_data['name'],
                    role=user_data['role'],
                    hashed_password=pwd_context.hash(user_data['password']),
                    created_at=datetime.now()
                )
                db.add(user)
                await db.commit()
                print(f'Created user: {user.email} with role: {user.role} and id: {user.id}')
            else:
                # Update password for existing user
                user.hashed_password = pwd_context.hash(user_data['password'])
                await db.commit()
                print(f'Updated password for user: {user.email} with role: {user.role} and id: {user.id}')
        break  # Exit after first iteration

if __name__ == "__main__":
    asyncio.run(create_test_users()) 