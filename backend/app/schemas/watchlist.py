from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.movie import MovieRead

class WatchlistRead(BaseModel):
    id: int
    movie_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class WatchlistMovieRead(BaseModel):
    id: int
    title: str
    original_title: str
    release_date: datetime | None
    model_config = ConfigDict(from_attributes=True)

class WatchlistItemRead(WatchlistRead):
    id: int
    created_at: datetime
    movie: MovieRead
    model_config = ConfigDict(from_attributes=True)