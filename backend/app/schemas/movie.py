from datetime import datetime, date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.genre import GenreRead


class MovieBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str = Field(..., max_length=200)
    original_title: str | None = Field(None, max_length=200)
    description: str | None = None
    release_year: int | None = Field(None, ge=1800, le=2100)
    release_date: datetime | None = None
    duration_minutes: int | None = Field(default=None, gt=0, le=1000)
    rating: float | None = None
    
class MovieCreate(MovieBase):
    genre_ids: list[int] | None = Field(default_factory=list)

class MovieExternalIdRead(BaseModel):
    provider: Literal["tmdb", "imdb"]
    external_id: str

    model_config = ConfigDict(from_attributes=True)

class MovieRead(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime
    genres: list[GenreRead] = Field(default_factory=list)
    external_ids: list[MovieExternalIdRead] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)
    
class MovieUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    original_title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, min_length=2, max_length=500)
    release_year: int | None = Field(default=None, ge=1800, le=2100)
    release_date: date | None = Field(default=None)
    duration_minutes: int | None = Field(default=None, gt=0)
    rating: float | None = Field(default=None, ge=0, le=10)