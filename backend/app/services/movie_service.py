from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.movie import Movie
from app.schemas.movie import MovieCreate

def create_movie(db: Session, movie_create: MovieCreate) -> Movie:
    movie = Movie(
        title=movie_create.title,
        original_title=movie_create.original_title,
        description=movie_create.description,
        release_year=movie_create.year,
        release_date=movie_create.release_date,
        duration_minutes=movie_create.duration_minutes,
        rating=movie_create.rating
    )
    
    db.add(movie)
    db.commit()
    db.refresh(movie)
    
    return movie

def get_movies(db: Session) -> list[Movie]:
    statement = select(Movie).order_by(Movie.id)
    return list(db.scalars(statement).all())

def get_movie_by_id(db: Session, movie_id: int) -> Movie | None:
    return db.get(Movie, movie_id)