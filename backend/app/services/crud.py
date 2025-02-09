from sqlalchemy.orm import Session
from app.models import user

def get_user(db: Session, user_id: int):
    return db.query(user.User).filter(user.User.id == user_id).first()


# def get_user(db: Session, user_id: int):
#     return db.query(User).filter(User.id == user_id).first()
