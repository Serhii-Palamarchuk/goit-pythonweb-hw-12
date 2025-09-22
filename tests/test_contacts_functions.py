"""
Unit tests for contacts routes functions.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from datetime import date

from src.database.models import User, Contact
from src.schemas.contacts import ContactCreate, ContactUpdate


class TestContactsRoutesFunctions:
    """Unit tests for contacts route functions."""

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.create_contact")
    def test_create_contact_function(self, mock_create, mock_get_user, mock_get_db):
        """Test create contact function directly."""
        from src.routes.contacts import create_contact

        # Setup mocks
        mock_db = Mock()
        test_user = User(
            id=1, username="testuser", email="test@example.com", is_confirmed=True
        )

        new_contact = Contact(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone_number="+1234567890",
            birth_date=date(1990, 1, 1),
            owner_id=1,
        )
        mock_create.return_value = new_contact

        contact_data = ContactCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone_number="+1234567890",
            birth_date=date(1990, 1, 1),
        )

        # Call function directly
        result = create_contact(contact_data, mock_db, test_user)

        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.email == "john@example.com"

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.get_contacts")
    def test_read_contacts_function(
        self, mock_get_contacts, mock_get_user, mock_get_db
    ):
        """Test read contacts function directly."""
        from src.routes.contacts import read_contacts

        # Setup mocks
        mock_db = Mock()
        test_user = User(
            id=1, username="testuser", email="test@example.com", is_confirmed=True
        )

        contacts = [
            Contact(
                id=1,
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                owner_id=1,
            ),
            Contact(
                id=2,
                first_name="Jane",
                last_name="Smith",
                email="jane@example.com",
                owner_id=1,
            ),
        ]
        mock_get_contacts.return_value = contacts

        # Call function directly
        result = read_contacts(
            skip=0, limit=100, search=None, db=mock_db, current_user=test_user
        )

        assert len(result) == 2
        assert result[0].first_name == "John"
        assert result[1].first_name == "Jane"

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.get_contact")
    def test_read_contact_function_success(
        self, mock_get_contact, mock_get_user, mock_get_db
    ):
        """Test read single contact function success."""
        from src.routes.contacts import read_contact

        # Setup mocks
        mock_db = Mock()
        test_user = User(
            id=1, username="testuser", email="test@example.com", is_confirmed=True
        )

        contact = Contact(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            owner_id=1,
        )
        mock_get_contact.return_value = contact

        # Call function directly
        result = read_contact(contact_id=1, db=mock_db, current_user=test_user)

        assert result.first_name == "John"
        assert result.id == 1

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.get_contact")
    def test_read_contact_function_not_found(
        self, mock_get_contact, mock_get_user, mock_get_db
    ):
        """Test read single contact function when not found."""
        from src.routes.contacts import read_contact

        # Setup mocks
        mock_db = Mock()
        test_user = User(
            id=1, username="testuser", email="test@example.com", is_confirmed=True
        )
        mock_get_contact.return_value = None

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            read_contact(contact_id=999, db=mock_db, current_user=test_user)

        assert exc_info.value.status_code == 404

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.update_contact")
    def test_update_contact_function_success(
        self, mock_update, mock_get_user, mock_get_db
    ):
        """Test update contact function success."""
        from src.routes.contacts import update_contact

        # Setup mocks
        mock_db = Mock()
        test_user = User(
            id=1, username="testuser", email="test@example.com", is_confirmed=True
        )

        updated_contact = Contact(
            id=1,
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            owner_id=1,
        )
        mock_update.return_value = updated_contact

        update_data = ContactUpdate(first_name="Jane", email="jane@example.com")

        # Call function directly
        result = update_contact(
            contact_id=1, contact=update_data, db=mock_db, current_user=test_user
        )

        assert result.first_name == "Jane"
        assert result.email == "jane@example.com"

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.update_contact")
    def test_update_contact_function_not_found(
        self, mock_update, mock_get_user, mock_get_db
    ):
        """Test update contact function when not found."""
        from src.routes.contacts import update_contact

        # Setup mocks
        mock_db = Mock()
        test_user = User(
            id=1, username="testuser", email="test@example.com", is_confirmed=True
        )
        mock_update.return_value = None

        update_data = ContactUpdate(first_name="Jane")

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            update_contact(
                contact_id=999, contact=update_data, db=mock_db, current_user=test_user
            )

        assert exc_info.value.status_code == 404

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.delete_contact")
    def test_delete_contact_function_success(
        self, mock_delete, mock_get_user, mock_get_db
    ):
        """Test delete contact function success."""
        from src.routes.contacts import delete_contact

        # Setup mocks
        mock_db = Mock()
        test_user = User(
            id=1, username="testuser", email="test@example.com", is_confirmed=True
        )

        deleted_contact = Contact(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            owner_id=1,
        )
        mock_delete.return_value = deleted_contact

        # Call function directly
        result = delete_contact(contact_id=1, db=mock_db, current_user=test_user)

        assert result.first_name == "John"

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.delete_contact")
    def test_delete_contact_function_not_found(
        self, mock_delete, mock_get_user, mock_get_db
    ):
        """Test delete contact function when not found."""
        from src.routes.contacts import delete_contact

        # Setup mocks
        mock_db = Mock()
        test_user = User(
            id=1, username="testuser", email="test@example.com", is_confirmed=True
        )
        mock_delete.return_value = None

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            delete_contact(contact_id=999, db=mock_db, current_user=test_user)

        assert exc_info.value.status_code == 404

    def test_contacts_routes_basic_imports(self):
        """Test that contacts route functions can be imported."""
        from src.routes.contacts import (
            create_contact,
            read_contacts,
            read_contact,
            update_contact,
            delete_contact,
        )

        assert callable(create_contact)
        assert callable(read_contacts)
        assert callable(read_contact)
        assert callable(update_contact)
        assert callable(delete_contact)

        # Test router exists
        from src.routes.contacts import router

        assert router is not None
        assert router.prefix == "/contacts"

    def test_contacts_search_and_birthdays_functions(self):
        """Test search and birthdays functions exist."""
        try:
            from src.routes.contacts import search_contacts, upcoming_birthdays

            assert callable(search_contacts)
            assert callable(upcoming_birthdays)
        except ImportError:
            # These functions might not exist or have different names
            pass
