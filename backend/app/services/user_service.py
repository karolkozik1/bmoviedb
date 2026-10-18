from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

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

def update_user(db: Session, user: User, user_data: UserUpdate) -> User:
    update_data = user_data.model_dump(exclude_unset=True)
    new_password = update_data.pop("password", None)
    for field, value in update_data.items():
        setattr(user, field, value)
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.username is not None:
        user.username = user_data.username
    if new_password is not None:
        user.password_hash = hash_password(new_password)
    
    db.commit()
    db.refresh(user)
    
    return user

def email_used_by_another_user(db: Session, email: str, user_id: int) -> bool:
    statement = select(User).where(User.email == email, User.id != user_id)
    return db.execute(statement).scalar_one_or_none() is not None

def username_used_by_another_user(db: Session, username: str, user_id: int) -> bool:
    statement = select(User).where(User.username == username, User.id != user_id)
    return db.execute(statement).scalar_one_or_none() is not None

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user