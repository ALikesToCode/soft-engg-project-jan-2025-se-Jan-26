import asyncio
import argparse
from app.database import get_db, Base, engine
from app.models.user import User
from sqlalchemy.future import select
import uuid
from datetime import datetime, UTC
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def add_user(email, name, role, password):
    """
    Add a new user to the system or update an existing user.
    
    Args:
        email: User's email address
        name: User's display name
        role: User's role (student, faculty, or support)
        password: User's password
    """
    # Validate role
    valid_roles = ["student", "faculty", "support"]
    if role not in valid_roles:
        print(f"Error: Role must be one of {valid_roles}")
        return
    
    # Initialize database if needed
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Add or update user
    async for db in get_db():
        # Check if user already exists
        user = await db.execute(select(User).where(User.email == email))
        user = user.scalars().first()
        
        if not user:
            # Create new user
            user = User(
                id=uuid.uuid4(),
                email=email,
                name=name,
                role=role,
                hashed_password=pwd_context.hash(password),
                is_google_user=False,
                created_at=datetime.now(UTC)
            )
            db.add(user)
            await db.commit()
            print(f"Created user: {user.email} with role: {user.role} and id: {user.id}")
        else:
            # Update existing user
            user.name = name
            user.role = role
            user.hashed_password = pwd_context.hash(password)
            user.updated_at = datetime.now(UTC)
            await db.commit()
            print(f"Updated user: {user.email} with role: {user.role} and id: {user.id}")
        break  # Exit after first iteration

def main():
    parser = argparse.ArgumentParser(description="Add a user to the system")
    parser.add_argument("--email", required=True, help="User's email address")
    parser.add_argument("--name", required=True, help="User's display name")
    parser.add_argument("--role", default="student", choices=["student", "faculty", "support"], 
                        help="User's role (student, faculty, or support)")
    parser.add_argument("--password", required=True, help="User's password")
    
    args = parser.parse_args()
    
    asyncio.run(add_user(args.email, args.name, args.role, args.password))

if __name__ == "__main__":
    main() 