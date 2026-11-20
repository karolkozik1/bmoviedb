from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class ReviewCreate(BaseModel):
    rating_id: int
    content: str | None = Field(default=None, min_length=10, max_length=5000)

class ReviewUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=10, max_length=5000)

class ReviewRead(BaseModel):
    id: int
    user_id: int
    movie_id: int
    rating_id: int
    content: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)