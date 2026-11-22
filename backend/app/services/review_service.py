from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.review import Review


def get_review_by_user_and_movie(db: Session, user_id: int, movie_id: int) -> Review | None:
    statement = select(Review).where(Review.user_id == user_id, Review.movie_id == movie_id)
    return db.scalar(statement)


def get_review_for_movie(db: Session, movie_id: int) -> list[Review]:
    statement = (
        select(Review)
        .where(Review.movie_id == movie_id, Review.status == "approved")
        .order_by(Review.created_at.desc())
    )
    return list(db.scalars(statement).all())


def create_review(db: Session, user_id: int, movie_id: int, rating_id: int, content: str | None) -> Review:
    review = Review(user_id=user_id, movie_id=movie_id, rating_id=rating_id, content=content, status="pending")
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def update_review(db: Session, review: Review, content: str | None) -> Review:
    review.content = content
    review.status = "pending"
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review: Review) -> None:
    db.delete(review)
    db.commit()