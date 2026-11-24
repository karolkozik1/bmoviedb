from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.schemas.watchlist import WatchlistItemRead, WatchlistRead
from app.services import user_service, movie_service, watchlist_service

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

@router.post("/me/watchlist/{movie_id}", response_model=WatchlistItemRead, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(movie_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    movie = movie_service.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    
    existing_entry = watchlist_service.get_watchlist_entry(db, current_user.id, movie_id)
    if existing_entry:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Movie already in watchlist")
    
    watchlist_entry = watchlist_service.add_to_watchlist(db, current_user.id, movie_id)
    return watchlist_entry

@router.get("/me/watchlist", response_model=WatchlistRead)
def get_watchlist(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    watchlist_entries = watchlist_service.get_user_watchlist(db, current_user.id)
    return watchlist_entries

@router.delete("/me/watchlist/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(movie_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    watchlist_entry = watchlist_service.get_watchlist_entry(db, current_user.id, movie_id)
    if not watchlist_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found in watchlist")
    
    watchlist_service.remove_from_watchlist(db, watchlist_entry)
    return None