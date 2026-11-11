from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class RatingBase(BaseModel):
    rating: int = Field(ge=1, le=10)

class RatingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    movie_id: int
    rating: int
    created_at: datetime