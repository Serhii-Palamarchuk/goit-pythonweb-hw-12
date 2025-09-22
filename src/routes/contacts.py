from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.schemas.contacts import ContactCreate, ContactResponse, ContactUpdate
from src.services.auth import get_current_user
from src.exceptions import (
    ContactNotFoundError,
    handle_database_error,
)

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return repository_contacts.create_contact(
            db=db, contact=contact, user=current_user
        )
    except ContactNotFoundError:
        # Перекидаємо ContactNotFoundError далі
        raise
    except Exception as e:
        handle_database_error(e, "створення контакту")


@router.get("/", response_model=List[ContactResponse])
def read_contacts(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if search:
        contacts = repository_contacts.search_contacts(db, current_user, search)
    else:
        contacts = repository_contacts.get_contacts(
            db, current_user, skip=skip, limit=limit
        )
    return contacts


@router.get("/birthdays", response_model=List[ContactResponse])
def get_upcoming_birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return repository_contacts.get_upcoming_birthdays(db, current_user)


@router.get("/{contact_id}", response_model=ContactResponse)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_contact = repository_contacts.get_contact(
        db, contact_id=contact_id, user=current_user
    )
    if db_contact is None:
        raise ContactNotFoundError(contact_id)
    return db_contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        db_contact = repository_contacts.update_contact(
            db, contact_id=contact_id, contact=contact, user=current_user
        )
        if db_contact is None:
            raise ContactNotFoundError(contact_id)
        return db_contact
    except ContactNotFoundError:
        # Перекидаємо ContactNotFoundError далі
        raise
    except Exception as e:
        handle_database_error(e, "оновлення контакту")


@router.delete("/{contact_id}", response_model=ContactResponse)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_contact = repository_contacts.delete_contact(
        db, contact_id=contact_id, user=current_user
    )
    if db_contact is None:
        raise ContactNotFoundError(contact_id)
    return db_contact
