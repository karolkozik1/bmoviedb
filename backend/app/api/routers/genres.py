from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.genre import GenreCreate, GenreRead
from app.services import genre_service

router = APIRouter(prefix="/genres", tags=["genres"])

@router.get("", response_model=list[GenreRead])
def get_genres(db: Session = Depends(get_db)):
    return genre_service.get_genres(db)

@router.post("", response_model=GenreCreate, status_code=status.HTTP_201_CREATED)
def create_genre(genre_data: GenreCreate, db: Session = Depends(get_db)):
    existing_genre = genre_service.get_genre_by_name(db, genre_name=genre_data.name)
    if existing_genre:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Genre already exists")
    return genre_service.create_genre(db=db, genre_create=genre_data)

@router.get("/{genre_id}", response_model=GenreRead)
def get_genre(genre_id: int, db: Session = Depends(get_db)):
    genre = genre_service.get_genre_by_id(db=db, genre_id=genre_id)
    if not genre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    return genre

