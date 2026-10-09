from datetime import date

from pydantic import BaseModel, ConfigDict, Field

class PersonCreate(BaseModel):
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    birth_date: date | None = None
    death_date: date | None = None
    biography: str | None = None

class PersonRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    birth_date: date | None = None
    death_date: date | None = None
    biography: str | None = None

    model_config = ConfigDict(from_attributes=True)
    
class MoviePersonCreate(BaseModel):
    person_id: int
    role: str = Field(min_length=2, max_length=50)
    