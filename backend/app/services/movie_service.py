from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.genre import Genre
from app.models.movie import Movie
from app.models.movie_external_id import MovieExternalId
from app.schemas.movie import MovieCreate, MovieUpdate
from app.models.movie_person import MoviePerson
from app.models.person import Person
from app.models.rating import Rating

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
        rating=movie_create.rating,
        is_active=movie_create.is_active
    )
    
    db.add(movie)
    db.commit()
    db.refresh(movie)
    
    return movie



def get_movies(db: Session, 
               title: str | None = None, 
               release_year: int | None = None, 
               genre_id: int | None = None,
               person_id: int | None = None,
               role: str | None = None,
               min_rating: float | None = None,
               is_active: bool | None = None,
               skip: int = 0,
               limit: int = 30,
               sort_by: str = "title") -> list[Movie]:
    rating_stats = get_rating_stats_subquery()
    statement = (
        select(Movie, rating_stats.c.average_rating, rating_stats.c.rating_count)
        .outerjoin(rating_stats, Movie.id == rating_stats.c.movie_id)
        .options(
            selectinload(Movie.genres),
            selectinload(Movie.people_roles).selectinload(MoviePerson.person),
            selectinload(Movie.external_ids),
        )
    )
    if sort_by == "release_year":
        statement = statement.order_by(Movie.release_year)
    elif sort_by == "newest":
        statement = statement.order_by(Movie.release_date.desc())
    elif sort_by == "oldest":
        statement = statement.order_by(Movie.release_date.asc())
    elif sort_by == "rating":
        statement = statement.order_by(rating_stats.c.average_rating.desc().nullslast())
    elif sort_by == "rating_asc":
        statement = statement.order_by(rating_stats.c.average_rating.asc().nullslast())
    elif sort_by == "rating_count":
        statement = statement.order_by(rating_stats.c.rating_count.desc().nullslast())
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
    if person_id is not None or role is not None:
        statement = statement.join(Movie.people_roles)
    if person_id is not None:
        statement = statement.where(MoviePerson.person_id == person_id)
    if role is not None:
        statement = statement.where(MoviePerson.role == role)
    if is_active is not None:
        statement = statement.where(Movie.is_active == is_active)
    statement = statement.offset(skip).limit(limit)
    if min_rating is not None:
        statement = statement.where(rating_stats.c.average_rating >= min_rating)
        
    rows = db.execute(statement).unique().all()
    movies = []
    for movie, average_rating, rating_count in rows:
        setattr(movie, "average_rating", round(float(average_rating), 2) if average_rating is not None else None)
        setattr(movie, "rating_count", rating_count if rating_count is not None else 0)
        movies.append(movie)
    return movies

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
    rating_stats = get_rating_stats_subquery()
    statement = (
        select(
            Movie,
            rating_stats.c.average_rating,
            rating_stats.c.rating_count,
        )
        .outerjoin(rating_stats, rating_stats.c.movie_id == Movie.id)
        .options(
            selectinload(Movie.genres),
            selectinload(Movie.people_roles).selectinload(MoviePerson.person),
            selectinload(Movie.external_ids),
        )
        .where(Movie.id == movie_id)
    )
    row = db.execute(statement).unique().first()
    
    if row is None:
        return None
    
    movie, average_rating, rating_count = row
    setattr(movie, "average_rating", round(float(average_rating), 2) if average_rating is not None else None)
    setattr(movie, "rating_count", rating_count if rating_count is not None else 0)
    
    return movie

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

def add_person_to_movie(db: Session, movie: Movie, person_id: int, role: str) -> MoviePerson:
    person = db.get(Person, person_id)
    if person is None:
        raise ValueError(f"Person with ID {person_id} does not exist")
    
    movie_person = MoviePerson(movie_id=movie.id, person_id=person.id, role=role)
    db.add(movie_person)
    db.commit()
    db.refresh(movie_person)
    return movie_person

def remove_person_from_movie(db: Session, movie: Movie, person_id: int, role: str) -> bool:
    statement = select(MoviePerson).where(
        MoviePerson.movie_id == movie.id,
        MoviePerson.person_id == person_id,
        MoviePerson.role == role)
    relation = db.scalars(statement).first()
    if relation is None:
        return False
    
    db.delete(relation)
    db.commit()
    return True

def get_rating_stats_subquery():
    return (
        select(
            Rating.movie_id.label("movie_id"),
            func.avg(Rating.rating).label("average_rating"),
            func.count(Rating.id).label("rating_count")
        )
        .group_by(Rating.movie_id)
        .subquery()
    )