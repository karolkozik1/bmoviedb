from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.execute(select(User).where(User.username == username)).scalar_one_or_none()

def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(email=user_data.email, 
                username=user_data.username, 
                password_hash=hash_password(user_data.password), 
                role="user", 
                trust_score=0, 
                is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user