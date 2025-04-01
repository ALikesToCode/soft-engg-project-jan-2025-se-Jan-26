import asyncio
import os
import sys
import uuid
from datetime import datetime, UTC
from passlib.context import CryptContext

# Add project directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, async_session
from app.models.user import User
from app.models.role import Role
from sqlalchemy import select, text

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_faculty_users():
    """Create faculty users with proper role assignments"""
    print("Creating faculty users...")
    
    # Ensure roles exist
    async with async_session() as session:
        # Check if faculty role exists
        result = await session.execute(select(Role).filter(Role.name == "faculty"))
        faculty_role = result.scalar_one_or_none()
        
        # Create faculty role if it doesn't exist
        if not faculty_role:
            print("Creating faculty role...")
            faculty_role = Role(name="faculty")
            session.add(faculty_role)
            await session.commit()
            
            # Refresh to get the ID
            await session.refresh(faculty_role)
        
        # Create faculty users
        faculty_emails = [
            "faculty1@example.com",
            "faculty2@example.com",
            "faculty3@example.com",
            "faculty4@example.com",
            "faculty5@example.com"
        ]
        
        faculty_ids = []
        
        for i, email in enumerate(faculty_emails):
            # Check if user already exists
            result = await session.execute(select(User).filter(User.email == email))
            user = result.scalar_one_or_none()
            
            if user:
                print(f"User {email} already exists, skipping creation")
                faculty_ids.append(user.id)
                continue
            
            # Create new faculty user
            hashed_password = pwd_context.hash(f"faculty{i+1}")
            
            new_user = User(
                id=uuid.uuid4(),
                email=email,
                name=f"Faculty Member {i+1}",
                hashed_password=hashed_password,
                is_google_user=False,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            
            session.add(new_user)
            
            # Commit to get the ID
            await session.commit()
            await session.refresh(new_user)
            
            # Add faculty role to user
            await session.execute(
                text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
                {"user_id": new_user.id, "role_id": faculty_role.id}
            )
            
            await session.commit()
            print(f"Created faculty user: {email}")
            
            faculty_ids.append(new_user.id)
        
        print(f"Created {len(faculty_ids)} faculty users")
        return faculty_ids

async def main():
    try:
        await create_faculty_users()
        print("Faculty users creation completed")
    except Exception as e:
        print(f"Error creating faculty users: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 