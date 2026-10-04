from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MovieExternalId(Base):
    __tablename__ = "movie_external_ids"
    __table_args__ = (
        CheckConstraint(
            "provider IN ('tmdb', 'imdb')",
            name="ck_movie_external_ids_provider",
        ),
        UniqueConstraint(
            "provider", "external_id", name="uq_movie_external_ids_provider_id"
        ),
        UniqueConstraint(
            "movie_id", "provider", name="uq_movie_external_ids_movie_provider"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    external_id: Mapped[str] = mapped_column(String(64), nullable=False)

    movie = relationship("Movie", back_populates="external_ids")