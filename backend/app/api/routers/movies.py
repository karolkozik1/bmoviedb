from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.movie import MovieCreate, MovieRead
from app.services import movie_service

router = APIRouter(prefix="/movies", tags=["movies"])

##Create a new movie
@router.post("", response_model=MovieRead, status_code=status.HTTP_201_CREATED)

def create_movie(movie_data: MovieCreate, db: Session = Depends(get_db)):
    try:
        return movie_service.create_movie(db=db, movie_create=movie_data)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

##Get a list of movies
@router.get("", response_model=list[MovieRead])

def get_movies(db: Session = Depends(get_db)):
    return movie_service.get_movies(db)

##Get a movie by ID
@router.get("/{movie_id}", response_model=MovieRead)

def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie