from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user import User
from app.models.movie import Movie

class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="uq_ratings_user_movie"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="ratings")
    movie: Mapped["Movie"] = relationship("Movie", back_populates="ratings")