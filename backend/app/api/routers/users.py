from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserRead)
def update_me(user_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_data.email and user_service.email_used_by_another_user(db, user_data.email, current_user.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    if user_data.username and user_service.username_used_by_another_user(db, user_data.username, current_user.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
    
    updated_user = user_service.update_user(db, current_user, user_data)
    return updated_user