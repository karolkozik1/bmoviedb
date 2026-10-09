from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.movie import MovieCreate, MovieRead, MovieUpdate
from app.schemas.person import MoviePersonCreate
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

def get_movies(title: str | None = Query(default=None, min_length=2, max_length=200), 
               release_year: int | None = Query(default=None, ge=1800, le=2100),
               genre_id: int | None = Query(default=None, gt=0),
               skip: int = Query(default=0, ge=0),
               limit: int = Query(default=30, ge=1, le=100), 
               sort_by: str = Query(default="title", pattern="^(title|release_year|newest|oldest)$"),
               db: Session = Depends(get_db)):
    return movie_service.get_movies(db, title=title, release_year=release_year, genre_id=genre_id, skip=skip, limit=limit, sort_by=sort_by)

##Get a movie by ID
@router.get("/{movie_id}", response_model=MovieRead)

def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie

@router.put("/{movie_id}", response_model=MovieRead)
def update_movie(movie_id: int, movie_data: MovieUpdate, db: Session = Depends(get_db)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    try:
        return movie_service.update_movie(db=db, movie=movie, movie_update=movie_data)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    movie_service.delete_movie(db=db, movie=movie)

@router.post("/{movie_id}/people", response_model=MoviePersonCreate, status_code=status.HTTP_201_CREATED)
def add_person_to_movie(movie_id: int, person_data: MoviePersonCreate, db: Session = Depends(get_db)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    try:
        return movie_service.add_person_to_movie(db=db, movie=movie, person_id=person_data.person_id, role=person_data.role)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error