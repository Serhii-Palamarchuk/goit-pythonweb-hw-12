"""
Contact repository module.

This module provides database operations for Contact entities,
including CRUD operations, search functionality, and birthday tracking.
"""

from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import and_, extract
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas.contacts import ContactCreate, ContactUpdate


def get_contact(db: Session, contact_id: int, user: User) -> Optional[Contact]:
    """
    Retrieve a specific contact by ID for a given user.

    Args:
        db (Session): Database session
        contact_id (int): ID of the contact to retrieve
        user (User): User who owns the contact

    Returns:
        Optional[Contact]: The contact if found, None otherwise
    """
    return (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.owner_id == user.id)
        .first()
    )


def get_contacts(
    db: Session, user: User, skip: int = 0, limit: int = 100
) -> List[Contact]:
    """
    Retrieve a list of contacts for a user with pagination.

    Args:
        db (Session): Database session
        user (User): User who owns the contacts
        skip (int): Number of records to skip for pagination
        limit (int): Maximum number of records to return

    Returns:
        List[Contact]: List of contacts for the user
    """
    return (
        db.query(Contact)
        .filter(Contact.owner_id == user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def search_contacts(db: Session, user: User, query: str) -> List[Contact]:
    """
    Search contacts by first name, last name, or email.

    Args:
        db (Session): Database session
        user (User): User who owns the contacts
        query (str): Search query string

    Returns:
        List[Contact]: List of contacts matching the search criteria
    """
    return (
        db.query(Contact)
        .filter(
            Contact.owner_id == user.id,
            (Contact.first_name.ilike(f"%{query}%"))
            | (Contact.last_name.ilike(f"%{query}%"))
            | (Contact.email.ilike(f"%{query}%")),
        )
        .all()
    )


def get_upcoming_birthdays(db: Session, user: User) -> List[Contact]:
    """
    Get contacts with birthdays in the next 7 days.

    Args:
        db (Session): Database session
        user (User): User who owns the contacts

    Returns:
        List[Contact]: List of contacts with upcoming birthdays
    """
    today = date.today()
    next_week = today + timedelta(days=7)

    # Handle year transitions
    if today.year == next_week.year:
        return (
            db.query(Contact)
            .filter(
                Contact.owner_id == user.id,
                and_(
                    extract("month", Contact.birth_date) >= today.month,
                    extract("month", Contact.birth_date) <= next_week.month,
                    extract("day", Contact.birth_date) >= today.day,
                    extract("day", Contact.birth_date) <= next_week.day,
                ),
            )
            .all()
        )
    else:
        # Handle case when the week spans across years
        return (
            db.query(Contact)
            .filter(
                Contact.owner_id == user.id,
                (
                    and_(
                        extract("month", Contact.birth_date) == today.month,
                        extract("day", Contact.birth_date) >= today.day,
                    )
                )
                | (
                    and_(
                        extract("month", Contact.birth_date) == next_week.month,
                        extract("day", Contact.birth_date) <= next_week.day,
                    )
                ),
            )
            .all()
        )


def create_contact(db: Session, contact: ContactCreate, user: User) -> Contact:
    """
    Create a new contact for a user.

    Args:
        db (Session): Database session
        contact (ContactCreate): Contact data to create
        user (User): User who will own the contact

    Returns:
        Contact: The newly created contact
    """
    db_contact = Contact(**contact.dict(), owner_id=user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def update_contact(
    db: Session, contact_id: int, contact: ContactUpdate, user: User
) -> Optional[Contact]:
    """
    Update an existing contact for a user.

    Args:
        db (Session): Database session
        contact_id (int): ID of the contact to update
        contact (ContactUpdate): Updated contact data
        user (User): User who owns the contact

    Returns:
        Optional[Contact]: The updated contact if found and updated, None otherwise
    """
    db_contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.owner_id == user.id)
        .first()
    )
    if db_contact:
        contact_data = contact.dict(exclude_unset=True)
        for field, value in contact_data.items():
            setattr(db_contact, field, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int, user: User) -> Optional[Contact]:
    """
    Delete a contact for a user.

    Args:
        db (Session): Database session
        contact_id (int): ID of the contact to delete
        user (User): User who owns the contact

    Returns:
        Optional[Contact]: The deleted contact if found and deleted, None otherwise
    """
    db_contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.owner_id == user.id)
        .first()
    )
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact
