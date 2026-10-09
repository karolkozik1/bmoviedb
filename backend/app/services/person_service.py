from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.person import Person
from app.schemas.person import PersonCreate

def get_people(db: Session) -> List[Person]:
    statement = (select(Person).order_by(Person.last_name, Person.first_name))
    return list(db.scalars(statement).all())

def get_person_by_id(db: Session, person_id: int) -> Person | None:
    return db.get(Person, person_id)

def create_person(db: Session, person_data: PersonCreate) -> Person:
    person = Person(first_name=person_data.first_name, last_name=person_data.last_name, birth_date=person_data.birth_date, death_date=person_data.death_date, biography=person_data.biography)
    db.add(person)
    db.commit()
    db.refresh(person)
    return person