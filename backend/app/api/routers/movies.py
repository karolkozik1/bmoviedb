from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.movie import MovieCreate, MovieRead, MovieUpdate
from app.schemas.person import MoviePersonCreate
from app.schemas.rating import RatingCreate, RatingRead
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.services import movie_service
from app.services import rating_service
from app.services import review_service

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
               person_id: int | None = Query(default=None, gt=0),
               role: str | None = Query(default=None, min_length=2, max_length=50),
               min_rating: float | None = Query(default=None, ge=0.0, le=10.0),
               skip: int = Query(default=0, ge=0),
               limit: int = Query(default=30, ge=1, le=100), 
               sort_by: str = Query(default="title", pattern="^(title|release_year|newest|oldest|rating|rating_asc|rating_count)$"),
               is_active: bool | None = Query(default=None),
               db: Session = Depends(get_db)):
    return movie_service.get_movies(db, title=title, release_year=release_year, genre_id=genre_id, person_id=person_id, role=role, min_rating=min_rating, skip=skip, limit=limit, sort_by=sort_by, is_active=is_active)

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
    
@router.delete("/{movie_id}/people/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_person_from_movie(movie_id: int, person_id: int, role: str, db: Session = Depends(get_db)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    removed = movie_service.remove_person_from_movie(db=db, movie=movie, person_id=person_id, role=role)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie person relation not found")
    
@router.post("/{movie_id}/ratings", response_model=RatingRead, status_code=status.HTTP_201_CREATED)
def rate_movie(movie_id: int, rating_data: RatingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    try:
        rating = rating_service.create_or_update_rating(db=db, user_id=current_user.id, movie_id=movie_id, value=rating_data.rating)
        return rating
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    
@router.get("/{movie_id}/ratings/summary")
def get_movie_ratings_summary(movie_id: int, db: Session = Depends(get_db)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    average, count = rating_service.get_movie_rating_average(db=db, movie_id=movie_id)
    return {"movie_id": movie_id, "average_rating": round(average, 2) if average is not None else None, "rating_count": count}

@router.get("/{movie_id}/ratings/me", response_model=RatingRead | None)
def get_my_rating(movie_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    rating = rating_service.get_user_rating(db=db, user_id=current_user.id, movie_id=movie_id)
    return rating

@router.delete("/{movie_id}/ratings/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_rating(movie_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    rating = rating_service.get_user_rating(db=db, user_id=current_user.id, movie_id=movie_id)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    rating_service.delete_user_rating(db=db, user_id=current_user.id, movie_id=movie_id)

@router.post("/{movie_id}/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(movie_id: int, review_data: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    existing_review = review_service.get_review_by_user_and_movie(
        db=db, user_id=current_user.id, movie_id=movie_id
    )
    if existing_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has already submitted a review for this movie")

    rating = rating_service.get_user_rating(db=db, user_id=current_user.id, movie_id=movie_id)
    if not rating:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User must rate the movie before submitting a review")

    if review_data.rating_id != rating.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Review rating must match the user's rating for this movie")

    review = review_service.create_review(db=db, user_id=current_user.id, movie_id=movie_id, rating_id=rating.id, content=review_data.content)
    return review


@router.get("/{movie_id}/reviews", response_model=list[ReviewRead])
def get_reviews(movie_id: int, db: Session = Depends(get_db)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    reviews = review_service.get_review_for_movie(db=db, movie_id=movie_id)
    return reviews


@router.get("/{movie_id}/reviews/me", response_model=ReviewRead | None)
def get_my_review(movie_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    review = review_service.get_review_by_user_and_movie(db=db, user_id=current_user.id, movie_id=movie_id)
    return review


@router.patch("/{movie_id}/reviews/me", response_model=ReviewRead)
def update_my_review(movie_id: int, review_data: ReviewUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    review = review_service.get_review_by_user_and_movie(db=db, user_id=current_user.id, movie_id=movie_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    updated_review = review_service.update_review(db=db, review=review, content=review_data.content)
    return updated_review


@router.delete("/{movie_id}/reviews/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_review(movie_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    movie = movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    review = review_service.get_review_by_user_and_movie(db=db, user_id=current_user.id, movie_id=movie_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    review_service.delete_review(db=db, review=review)