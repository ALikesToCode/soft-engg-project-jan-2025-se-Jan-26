from app.models.user import User
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_or_create_user(db: AsyncSession, user_data: dict):
    print(user_data)
    
    # Fetch user from the database
    result = await db.execute(select(User).where(User.email == user_data["email"]))
    user = result.scalars().first()  # Get first user if exists, else None

    if user:
        print("User already exists")
        return user
    else:
        print("Creating new user")
        new_user = User(
            first_name=user_data.get("given_name"),
            last_name=user_data.get("family_name"),
            email=user_data.get("email"),
            picture=user_data.get("picture"),
            name=user_data.get("name"),
            at_hash=user_data.get("at_hash")
        )
        db.add(new_user)
        await db.commit()  # Commit changes to DB
        await db.refresh(new_user)  # Refresh to get the latest data
        return new_user
    
# async def get_or_create_user(db, user_data: dict):
#     print(user_data)
#     user = await db.execute(select(User).where(User.email == user_data["email"]))
#     if user.scalars().first():
#         print("User already exists")
#     else:
#         print("Creating new user")
