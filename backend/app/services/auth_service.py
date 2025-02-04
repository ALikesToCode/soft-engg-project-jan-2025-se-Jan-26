from app.models.user import User
from sqlalchemy.future import select

async def get_or_create_user(db, user_data: dict):
    print(user_data)
    user = await db.execute(select(User).where(User.email == user_data["email"]))
    if user.scalars().first():
        print("User already exists")
    else:
        print("Creating new user")
