from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.genre import Genre
from app.models.movie import Movie
from app.models.movie_external_id import MovieExternalId
from app.schemas.movie import MovieCreate, MovieUpdate

def create_movie(db: Session, movie_create: MovieCreate) -> Movie:
    genre_ids = movie_create.genre_ids or []
    unique_genre_ids = set(genre_ids)
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



def get_movies(db: Session, 
               title: str | None = None, 
               release_year: int | None = None, 
               genre_id: int | None = None,
               skip: int = 0,
               limit: int = 30,
               sort_by: str = "title") -> list[Movie]:
    statement = select(Movie).options(
        selectinload(Movie.genres), selectinload(Movie.external_ids)
    )
    if sort_by == "release_year":
        statement = statement.order_by(Movie.release_year)
    elif sort_by == "newest":
        statement = statement.order_by(Movie.release_date.desc())
    elif sort_by == "oldest":
        statement = statement.order_by(Movie.release_date.asc())
    else:
        statement = statement.order_by(Movie.title)
    if title:
        statement = statement.where(
            or_(Movie.title.ilike(f"%{title}%"), 
                Movie.original_title.ilike(f"%{title}%")))
    if release_year:
        statement = statement.where(Movie.release_year == release_year)
    if genre_id:
        statement = statement.join(Movie.genres).where(Genre.id == genre_id)
    statement = statement.offset(skip).limit(limit)
    return list(db.scalars(statement).unique().all())

def update_movie(db: Session, movie: Movie, movie_update: MovieUpdate) -> Movie:
    update_data = movie_update.model_dump(exclude_unset=True)
    genre_ids = update_data.pop("genre_ids", None)
    
    for field, value in update_data.items():
        setattr(movie, field, value)
    
    if genre_ids is not None:
        unique_genre_ids = set(genre_ids)
        genres = get_genres_by_ids(db, list(unique_genre_ids))
        found_genre_ids = {genre.id for genre in genres}
        missing_genre_ids = unique_genre_ids - found_genre_ids
        if len(genres) != len(unique_genre_ids):
            raise ValueError(f"Duplicate genre IDs: {sorted(unique_genre_ids - {genre.id for genre in genres})}")
        if missing_genre_ids:
            raise ValueError(f"Unknown genre IDs: {sorted(missing_genre_ids)}")
        movie.genres = genres
    db.commit()
    db.refresh(movie)
    return movie

def delete_movie(db: Session, movie: Movie) -> None:
    db.delete(movie)
    db.commit()

def get_movie_by_id(db: Session, movie_id: int) -> Movie | None:
    statement = select(Movie).options(
        selectinload(Movie.genres), selectinload(Movie.external_ids)
    ).where(Movie.id == movie_id)
    return db.scalars(statement).first()

def upsert_imported_movie(
    db: Session,
    provider: str,
    external_id: str,
    movie_data: MovieCreate,
) -> Movie:
    provider = provider.strip().lower()
    external_id = external_id.strip()
    if provider not in {"tmdb", "imdb"}:
        raise ValueError("Provider must be 'tmdb' or 'imdb'")
    if not external_id:
        raise ValueError("External ID cannot be empty")

    genre_ids = set(movie_data.genre_ids or [])
    genres = get_genres_by_ids(db, list(genre_ids))
    found_genre_ids = {genre.id for genre in genres}
    missing_genre_ids = genre_ids - found_genre_ids
    if missing_genre_ids:
        raise ValueError(f"Unknown genre IDs: {sorted(missing_genre_ids)}")

    external_record = db.scalars(
        select(MovieExternalId)
        .options(selectinload(MovieExternalId.movie))
        .where(
            MovieExternalId.provider == provider,
            MovieExternalId.external_id == external_id,
        )
    ).first()
    movie_values = movie_data.model_dump(exclude={"genre_ids"})

    if external_record:
        movie = external_record.movie
        for field, value in movie_values.items():
            setattr(movie, field, value)
        movie.genres = genres
    else:
        movie = Movie(**movie_values, genres=genres)
        db.add(movie)
        db.flush()
        db.add(
            MovieExternalId(
                movie_id=movie.id,
                provider=provider,
                external_id=external_id,
            )
        )

    db.commit()
    db.refresh(movie)
    return movie

def get_genres_by_ids(db: Session, genre_ids: list[int]) -> list[Genre]:
    if not genre_ids:
        return []
    statement = select(Genre).where(Genre.id.in_(genre_ids))
    return list(db.scalars(statement).all())