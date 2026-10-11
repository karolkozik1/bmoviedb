from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

# class MovieRole(str, Enum):
#     ACTOR = "actor"
#     DIRECTOR = "director"
#     PRODUCER = "producer"
#     WRITER = "writer"
#     CINEMATOGRAPHER = "cinematographer"
#     EDITOR = "editor"
#     COMPOSER = "composer"

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

class MoviePersonRead(BaseModel):
    role:str
    person: PersonRead
    
    model_config = ConfigDict(from_attributes=True)