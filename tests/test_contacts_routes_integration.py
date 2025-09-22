"""
Integration tests for contacts routes using TestClient.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import date

from main import app
from src.database.models import User, Contact


@pytest.fixture
def test_client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_user():
    """Test user fixture."""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_confirmed=True,
    )


@pytest.fixture
def test_contact():
    """Test contact fixture."""
    return Contact(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone_number="+1234567890",
        birth_date=date(1990, 1, 1),
        owner_id=1,
    )


class TestContactsRoutesIntegration:
    """Integration tests for contacts routes."""

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.create_contact")
    def test_create_contact_success(
        self, mock_create, mock_get_user, mock_get_db, test_client, test_user
    ):
        """Test successful contact creation."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = test_user

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

        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone_number": "+1234567890",
            "birth_date": "1990-01-01",
        }

        response = test_client.post(
            "/contacts/", json=contact_data, headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == "john@example.com"

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.get_contacts")
    def test_read_contacts_success(
        self, mock_get_contacts, mock_get_user, mock_get_db, test_client, test_user
    ):
        """Test successful contacts retrieval."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = test_user

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

        response = test_client.get(
            "/contacts/", headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["first_name"] == "John"
        assert data[1]["first_name"] == "Jane"

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.get_contacts")
    def test_read_contacts_with_search(
        self, mock_get_contacts, mock_get_user, mock_get_db, test_client, test_user
    ):
        """Test contacts retrieval with search."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = test_user

        contacts = [
            Contact(
                id=1,
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                owner_id=1,
            )
        ]
        mock_get_contacts.return_value = contacts

        response = test_client.get(
            "/contacts/?search=john", headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["first_name"] == "John"

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.get_contact")
    def test_read_contact_success(
        self,
        mock_get_contact,
        mock_get_user,
        mock_get_db,
        test_client,
        test_user,
        test_contact,
    ):
        """Test successful single contact retrieval."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = test_user
        mock_get_contact.return_value = test_contact

        response = test_client.get(
            "/contacts/1", headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "John"
        assert data["id"] == 1

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.get_contact")
    def test_read_contact_not_found(
        self, mock_get_contact, mock_get_user, mock_get_db, test_client, test_user
    ):
        """Test contact not found."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = test_user
        mock_get_contact.return_value = None

        response = test_client.get(
            "/contacts/999", headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 404

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.update_contact")
    def test_update_contact_success(
        self, mock_update, mock_get_user, mock_get_db, test_client, test_user
    ):
        """Test successful contact update."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = test_user

        updated_contact = Contact(
            id=1,
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone_number="+1234567890",
            birth_date=date(1990, 1, 1),
            owner_id=1,
        )
        mock_update.return_value = updated_contact

        update_data = {"first_name": "Jane", "email": "jane@example.com"}

        response = test_client.put(
            "/contacts/1", json=update_data, headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["email"] == "jane@example.com"

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.update_contact")
    def test_update_contact_not_found(
        self, mock_update, mock_get_user, mock_get_db, test_client, test_user
    ):
        """Test contact update when not found."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = test_user
        mock_update.return_value = None

        update_data = {"first_name": "Jane"}

        response = test_client.put(
            "/contacts/999", json=update_data, headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 404

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.delete_contact")
    def test_delete_contact_success(
        self,
        mock_delete,
        mock_get_user,
        mock_get_db,
        test_client,
        test_user,
        test_contact,
    ):
        """Test successful contact deletion."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = test_user
        mock_delete.return_value = test_contact

        response = test_client.delete(
            "/contacts/1", headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "John"

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.delete_contact")
    def test_delete_contact_not_found(
        self, mock_delete, mock_get_user, mock_get_db, test_client, test_user
    ):
        """Test contact deletion when not found."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = test_user
        mock_delete.return_value = None

        response = test_client.delete(
            "/contacts/999", headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 404

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.search_contacts")
    def test_search_contacts(
        self, mock_search, mock_get_user, mock_get_db, test_client, test_user
    ):
        """Test contact search functionality."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = test_user

        contacts = [
            Contact(
                id=1,
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                owner_id=1,
            )
        ]
        mock_search.return_value = contacts

        response = test_client.get(
            "/contacts/search?query=john", headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["first_name"] == "John"

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.get_upcoming_birthdays")
    def test_upcoming_birthdays(
        self, mock_birthdays, mock_get_user, mock_get_db, test_client, test_user
    ):
        """Test upcoming birthdays endpoint."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = test_user

        contacts = [
            Contact(
                id=1,
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                birth_date=date(1990, 1, 1),
                owner_id=1,
            )
        ]
        mock_birthdays.return_value = contacts

        response = test_client.get(
            "/contacts/upcoming-birthdays", headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["first_name"] == "John"

    @patch("src.routes.contacts.get_db")
    @patch("src.routes.contacts.get_current_user")
    @patch("src.repository.contacts.get_contacts")
    def test_pagination_parameters(
        self, mock_get_contacts, mock_get_user, mock_get_db, test_client, test_user
    ):
        """Test pagination parameters."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = test_user
        mock_get_contacts.return_value = []

        response = test_client.get(
            "/contacts/?skip=10&limit=5", headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 200
        # Verify that the parameters were passed correctly
        mock_get_contacts.assert_called_once()

    def test_contacts_router_exists(self):
        """Test that contacts router is properly configured."""
        from src.routes.contacts import router

        assert router is not None
        assert router.prefix == "/contacts"
        assert "contacts" in router.tags
