from typing import List
from sqlalchemy import String, and_, cast, func, or_, select
from sqlalchemy.orm import Session

from app.models.person import Person
from app.schemas.person import PersonCreate, PersonUpdate

def get_people(db: Session, search: str | None) -> List[Person]:
    statement = select(Person)
    if search:
        search_terms = search.strip().split()
        conditions = []
        for term in search_terms:
            pattern = f"%{term}%"
            full_name = func.concat(Person.first_name, " ", Person.last_name)
            conditions.append(or_(Person.first_name.ilike(pattern), Person.last_name.ilike(pattern), full_name.ilike(pattern)))
        statement = statement.where(and_(*conditions))
    return list(db.scalars(statement.order_by(Person.last_name, Person.first_name)).all())

def get_person_by_id(db: Session, person_id: int) -> Person | None:
    return db.get(Person, person_id)

def create_person(db: Session, person_data: PersonCreate) -> Person:
    person = Person(first_name=person_data.first_name, last_name=person_data.last_name, birth_date=person_data.birth_date, death_date=person_data.death_date, biography=person_data.biography)
    db.add(person)
    db.commit()
    db.refresh(person)
    return person

def update_person(db: Session, person: Person, person_data: PersonUpdate) -> Person:
    update_data = person_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(person, field, value)
    db.commit()
    db.refresh(person)
    return person

def delete_person(db: Session, person: Person) -> None:
    db.delete(person)
    db.commit()