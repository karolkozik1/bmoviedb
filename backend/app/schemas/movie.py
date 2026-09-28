from datetime import datetime

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

class MovieRead(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime
    genres: list[GenreRead] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)