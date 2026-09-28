from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.genre import Genre
from app.schemas.genre import GenreCreate

def get_genres(db: Session) -> list[Genre]:
    statement = select(Genre).order_by(Genre.name)
    return list(db.scalars(statement).all())

def get_genre_by_id(db: Session, genre_id: int) -> Genre | None:
    return db.get(Genre, genre_id)

def get_genre_by_name(db: Session, genre_name: str) -> Genre | None:
    statement = select(Genre).where(Genre.name == genre_name)
    return db.scalars(statement).first()

def create_genre(db: Session, genre_create: GenreCreate) -> Genre:
    genre = Genre(name=genre_create.name)
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre