from datetime import datetime

from pydantic import BaseModel, ConfigDict

class MovieBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    original_title: str | None = None
    description: str | None = None
    year: int
    release_date: datetime | None = None
    duration_minutes: int | None = None
    rating: float | None = None
    
class MovieCreate(MovieBase):
    pass

class MovieRead(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)