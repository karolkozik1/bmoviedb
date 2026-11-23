from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.movie import Movie
from app.models.watchlist import Watchlist

def get_watchlist_entry(db: Session, user_id: int, movie_id: int) -> Watchlist | None:
    statement = select(Watchlist).where(Watchlist.user_id == user_id, Watchlist.movie_id == movie_id)
    return db.scalar(statement)

def add_to_watchlist(db: Session, user_id: int, movie_id: int) -> Watchlist:
    watchlist_entry = Watchlist(user_id=user_id, movie_id=movie_id)
    db.add(watchlist_entry)
    db.commit()
    db.refresh(watchlist_entry)
    return watchlist_entry

def get_user_watchlist(db: Session, user_id: int) -> list[Watchlist]:
    statement = (
        select(Watchlist).where(Watchlist.user_id == user_id)
        .options(selectinload(Watchlist.movie).selectinload(Movie.genres))
        .order_by(Watchlist.created_at.desc())
    )
    return list(db.scalars(statement).all())

def remove_from_watchlist(db: Session, watchlist_entry: Watchlist) -> None:
    db.delete(watchlist_entry)
    db.commit()