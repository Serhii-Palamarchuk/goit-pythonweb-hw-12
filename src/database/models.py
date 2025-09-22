"""
Database models for the Contacts API application.

This module contains SQLAlchemy models for User and Contact entities,
defining the database schema and relationships.
"""

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from src.database.db import Base


class UserRole(enum.Enum):
    """Enumeration of user roles in the system."""

    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    User model representing registered users in the system.

    This model stores user information including authentication data,
    profile information, and role-based access control.

    Attributes:
        id (int): Primary key, unique identifier for the user
        username (str): Unique username for the user
        email (str): Unique email address for the user
        hashed_password (str): Bcrypt hashed password
        is_verified (bool): Email verification status
        avatar (str): URL to user's avatar image
        role (UserRole): User's role (USER or ADMIN)
        created_at (datetime): Timestamp when user was created
        updated_at (datetime): Timestamp when user was last updated
        contacts (list): List of contacts owned by this user
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    avatar = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    contacts = relationship(
        "Contact", back_populates="owner", cascade="all, delete-orphan"
    )


class Contact(Base):
    """
    Contact model representing individual contacts in the system.

    This model stores contact information including personal details
    and relationships to the user who owns the contact.

    Attributes:
        id (int): Primary key, unique identifier for the contact
        first_name (str): Contact's first name
        last_name (str): Contact's last name
        email (str): Contact's email address
        phone_number (str): Contact's phone number
        birth_date (date): Contact's birth date
        additional_data (str): Optional additional information
        owner_id (int): Foreign key referencing the user who owns this contact
        owner (User): The user who owns this contact
    """

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, index=True)
    phone_number = Column(String(20), nullable=False)
    birth_date = Column(Date, nullable=False)
    additional_data = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="contacts")
