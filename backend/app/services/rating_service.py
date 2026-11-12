from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.rating import Rating

def get_user_rating(db: Session, user_id: int, movie_id: int) -> Rating | None:
    statement = select(Rating).where(Rating.user_id == user_id, Rating.movie_id == movie_id)
    return db.scalar(statement)

def create_or_update_rating(db: Session, user_id: int, movie_id: int, value: int) -> Rating:
    existing_rating = get_user_rating(db, user_id, movie_id)
    if existing_rating:
        existing_rating.rating = value
        db.add(existing_rating)
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    else:
        new_rating = Rating(user_id=user_id, movie_id=movie_id, rating=value)
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return new_rating


def get_movie_rating_average(db: Session, movie_id: int) -> tuple[float | None, int]:
    statement = select(func.avg(Rating.rating), func.count(Rating.rating)).where(Rating.movie_id == movie_id)
    result = db.scalar(statement).one()
    average = result[0]
    count = result[1]
    return (float(average) if average is not None else None, count)