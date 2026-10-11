from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.person import PersonRead, PersonCreate, PersonUpdate
from app.services import person_service

router = APIRouter(prefix="/people",tags=["people"],)

@router.get("", response_model=list[PersonRead])
def get_people(search: str | None = Query(default=None, min_length=2, max_length=200), db: Session = Depends(get_db)):
    people = person_service.get_people(db, search=search)
    return people

@router.get("/{person_id}", response_model=PersonRead)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = person_service.get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    return person

@router.post("", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
def create_person(person_data: PersonCreate, db: Session = Depends(get_db)):
    return person_service.create_person(db, person_data)

@router.put("/{person_id}", response_model=PersonRead)
def update_person(person_id: int, person_data: PersonUpdate, db: Session = Depends(get_db)):
    person = person_service.get_person_by_id(db, person_id)
    if person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    return person_service.update_person(db, person, person_data)