"""
Unit tests for contacts repository module.

These tests cover all CRUD operations and search functionality
for the contacts repository using pytest and SQLAlchemy.
"""

import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.models import Base, Contact, User, UserRole
from src.repository import contacts as contact_repo
from src.schemas.contacts import ContactCreate, ContactUpdate


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_verified=True,
        role=UserRole.USER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_contact_data():
    """Sample contact data for testing."""
    return ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="+1234567890",
        birth_date=date(1990, 5, 15),
        additional_data="Test contact",
    )


@pytest.fixture
def test_contact(db_session, test_user, test_contact_data):
    """Create a test contact."""
    contact = contact_repo.create_contact(db_session, test_contact_data, test_user)
    return contact


class TestContactRepository:
    """Test class for contact repository functions."""

    def test_create_contact(self, db_session, test_user, test_contact_data):
        """Test creating a new contact."""
        contact = contact_repo.create_contact(db_session, test_contact_data, test_user)

        assert contact.id is not None
        assert contact.first_name == test_contact_data.first_name
        assert contact.last_name == test_contact_data.last_name
        assert contact.email == test_contact_data.email
        assert contact.phone_number == test_contact_data.phone_number
        assert contact.birth_date == test_contact_data.birth_date
        assert contact.additional_data == test_contact_data.additional_data
        assert contact.owner_id == test_user.id

    def test_get_contact(self, db_session, test_user, test_contact):
        """Test retrieving a contact by ID."""
        retrieved_contact = contact_repo.get_contact(
            db_session, test_contact.id, test_user
        )

        assert retrieved_contact is not None
        assert retrieved_contact.id == test_contact.id
        assert retrieved_contact.first_name == test_contact.first_name

    def test_get_contact_not_found(self, db_session, test_user):
        """Test retrieving a non-existent contact."""
        contact = contact_repo.get_contact(db_session, 999, test_user)
        assert contact is None

    def test_get_contact_wrong_owner(self, db_session, test_contact):
        """Test retrieving a contact with wrong owner."""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password",
            is_verified=True,
            role=UserRole.USER,
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        # Try to get contact with wrong owner
        contact = contact_repo.get_contact(db_session, test_contact.id, other_user)
        assert contact is None

    def test_get_contacts(self, db_session, test_user):
        """Test retrieving all contacts for a user."""
        # Create multiple contacts
        contact_data = [
            ContactCreate(
                first_name=f"Contact{i}",
                last_name="Test",
                email=f"contact{i}@example.com",
                phone_number=f"+123456789{i}",
                birth_date=date(1990 + i, 1, 1),
                additional_data=f"Test contact {i}",
            )
            for i in range(3)
        ]

        for data in contact_data:
            contact_repo.create_contact(db_session, data, test_user)

        contacts = contact_repo.get_contacts(db_session, test_user)
        assert len(contacts) == 3

    def test_get_contacts_with_pagination(self, db_session, test_user):
        """Test retrieving contacts with pagination."""
        # Create 5 contacts
        for i in range(5):
            contact_data = ContactCreate(
                first_name=f"Contact{i}",
                last_name="Test",
                email=f"contact{i}@example.com",
                phone_number=f"+123456789{i}",
                birth_date=date(1990 + i, 1, 1),
                additional_data=f"Test contact {i}",
            )
            contact_repo.create_contact(db_session, contact_data, test_user)

        # Test pagination
        contacts_page1 = contact_repo.get_contacts(
            db_session, test_user, skip=0, limit=2
        )
        contacts_page2 = contact_repo.get_contacts(
            db_session, test_user, skip=2, limit=2
        )

        assert len(contacts_page1) == 2
        assert len(contacts_page2) == 2
        assert contacts_page1[0].id != contacts_page2[0].id

    def test_search_contacts(self, db_session, test_user):
        """Test searching contacts by name and email."""
        # Create contacts with different names
        contacts_data = [
            ContactCreate(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone_number="+1234567890",
                birth_date=date(1990, 1, 1),
                additional_data="Test",
            ),
            ContactCreate(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@test.com",
                phone_number="+1234567891",
                birth_date=date(1991, 1, 1),
                additional_data="Test",
            ),
            ContactCreate(
                first_name="Bob",
                last_name="Johnson",
                email="bob@example.org",
                phone_number="+1234567892",
                birth_date=date(1992, 1, 1),
                additional_data="Test",
            ),
        ]

        for data in contacts_data:
            contact_repo.create_contact(db_session, data, test_user)

        # Search by first name
        results = contact_repo.search_contacts(db_session, test_user, "John")
        assert len(results) >= 1
        assert any(c.first_name == "John" for c in results)

        # Search by last name
        results = contact_repo.search_contacts(db_session, test_user, "Smith")
        assert len(results) == 1
        assert results[0].last_name == "Smith"

        # Search by email
        results = contact_repo.search_contacts(db_session, test_user, "example.com")
        assert len(results) >= 1

        # Search with no results
        results = contact_repo.search_contacts(db_session, test_user, "nonexistent")
        assert len(results) == 0

    def test_get_upcoming_birthdays(self, db_session, test_user):
        """Test retrieving contacts with upcoming birthdays."""
        today = date.today()
        next_week = today + timedelta(days=7)

        # Create contacts with different birth dates
        contacts_data = [
            ContactCreate(
                first_name="Birthday1",
                last_name="Today",
                email="today@example.com",
                phone_number="+1234567890",
                birth_date=date(1990, today.month, today.day),
                additional_data="Birthday today",
            ),
            ContactCreate(
                first_name="Birthday2",
                last_name="NextWeek",
                email="nextweek@example.com",
                phone_number="+1234567891",
                birth_date=date(1991, next_week.month, next_week.day),
                additional_data="Birthday next week",
            ),
            ContactCreate(
                first_name="Birthday3",
                last_name="FarAway",
                email="faraway@example.com",
                phone_number="+1234567892",
                birth_date=date(1992, 12, 25),
                additional_data="Birthday far away",
            ),
        ]

        for data in contacts_data:
            contact_repo.create_contact(db_session, data, test_user)

        upcoming = contact_repo.get_upcoming_birthdays(db_session, test_user)

        # Should include birthdays today and within next 7 days
        assert len(upcoming) >= 1
        for contact in upcoming:
            birth_month_day = (contact.birth_date.month, contact.birth_date.day)
            today_month_day = (today.month, today.day)
            next_week_month_day = (next_week.month, next_week.day)

            # Check if birthday is within the range
            if today.year == next_week.year:
                assert (
                    birth_month_day >= today_month_day
                    and birth_month_day <= next_week_month_day
                )

    def test_update_contact(self, db_session, test_user, test_contact):
        """Test updating an existing contact."""
        update_data = ContactUpdate(
            first_name="UpdatedJohn", email="updated.john@example.com"
        )

        updated_contact = contact_repo.update_contact(
            db_session, test_contact.id, update_data, test_user
        )

        assert updated_contact is not None
        assert updated_contact.first_name == "UpdatedJohn"
        assert updated_contact.email == "updated.john@example.com"
        # Other fields should remain unchanged
        assert updated_contact.last_name == test_contact.last_name
        assert updated_contact.phone_number == test_contact.phone_number

    def test_update_contact_not_found(self, db_session, test_user):
        """Test updating a non-existent contact."""
        update_data = ContactUpdate(first_name="UpdatedName")

        result = contact_repo.update_contact(db_session, 999, update_data, test_user)
        assert result is None

    def test_delete_contact(self, db_session, test_user, test_contact):
        """Test deleting an existing contact."""
        contact_id = test_contact.id

        deleted_contact = contact_repo.delete_contact(db_session, contact_id, test_user)

        assert deleted_contact is not None
        assert deleted_contact.id == contact_id

        # Verify contact is actually deleted
        retrieved_contact = contact_repo.get_contact(db_session, contact_id, test_user)
        assert retrieved_contact is None

    def test_delete_contact_not_found(self, db_session, test_user):
        """Test deleting a non-existent contact."""
        result = contact_repo.delete_contact(db_session, 999, test_user)
        assert result is None
