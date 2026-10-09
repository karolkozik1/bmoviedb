from datetime import date

from sqlalchemy import Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=True)
    death_date: Mapped[date] = mapped_column(Date, nullable=True)
    biography: Mapped[str] = mapped_column(Text, nullable=True)

    movie_roles = relationship("MoviePerson", back_populates="persons", cascade="all, delete-orphan")