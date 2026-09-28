from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.genre import Genre
from app.models.movie import Movie
from app.schemas.movie import MovieCreate

def create_movie(db: Session, movie_create: MovieCreate) -> Movie:
    unique_genre_ids = set(movie_create.genre_ids)
    genres = get_genres_by_ids(db, list(unique_genre_ids))
    found_genre_ids = {genre.id for genre in genres}
    missing_genre_ids = unique_genre_ids - found_genre_ids
    if missing_genre_ids:
        raise ValueError(f"Unknown genre IDs: {sorted(missing_genre_ids)}")

    movie = Movie(
        title=movie_create.title,
        original_title=movie_create.original_title,
        description=movie_create.description,
        release_year=movie_create.release_year,
        release_date=movie_create.release_date,
        duration_minutes=movie_create.duration_minutes,
        genres=genres,
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
    statement = select(Movie).options(selectinload(Movie.genres)).where(Movie.id == movie_id)
    return db.scalars(statement).first()

def get_genres_by_ids(db: Session, genre_ids: list[int]) -> list[Genre]:
    if not genre_ids:
        return []
    statement = select(Genre).where(Genre.id.in_(genre_ids))
    return list(db.scalars(statement).all())