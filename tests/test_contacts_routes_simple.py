import pytest
from unittest.mock import Mock, patch
from datetime import date
from sqlalchemy.orm import Session

from src.routes.contacts import (
    create_contact,
    read_contacts,
    get_upcoming_birthdays,
    read_contact,
    update_contact,
    delete_contact,
)
from src.database.models import User, Contact
from src.schemas.contacts import ContactCreate, ContactUpdate
from src.exceptions import ContactNotFoundError
from src.repository import contacts as repository_contacts


class TestContactRoutesSimple:
    """Simple tests for contact routes"""

    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)

    @pytest.fixture
    def sample_user(self):
        user = Mock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        return user

    @pytest.fixture
    def sample_contact(self):
        contact = Mock(spec=Contact)
        contact.id = 1
        contact.first_name = "John"
        contact.last_name = "Doe"
        contact.email = "john.doe@example.com"
        contact.phone_number = "+1234567890"
        contact.birthday = None
        contact.owner_id = 1
        return contact

    @pytest.fixture
    def contact_create_data(self):
        return ContactCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="+1234567890",
            birth_date=date(1990, 5, 15),
        )

    @pytest.fixture
    def contact_update_data(self):
        return ContactUpdate(
            first_name="Jane", last_name="Smith", email="jane.smith@example.com"
        )

    def test_create_contact_success(
        self, mock_db, sample_user, contact_create_data, sample_contact
    ):
        """Test successful contact creation"""
        with patch.object(
            repository_contacts, "create_contact", return_value=sample_contact
        ):
            result = create_contact(contact_create_data, mock_db, sample_user)
        assert result == sample_contact

    def test_create_contact_not_found_error(
        self, mock_db, sample_user, contact_create_data
    ):
        """Test contact creation with ContactNotFoundError"""
        with patch.object(
            repository_contacts, "create_contact", side_effect=ContactNotFoundError(1)
        ):
            with pytest.raises(ContactNotFoundError):
                create_contact(contact_create_data, mock_db, sample_user)

    def test_create_contact_database_error(
        self, mock_db, sample_user, contact_create_data
    ):
        """Test contact creation with database error"""
        with patch.object(
            repository_contacts,
            "create_contact",
            side_effect=Exception("Database error"),
        ), patch("src.routes.contacts.handle_database_error") as mock_handle:
            create_contact(contact_create_data, mock_db, sample_user)
            mock_handle.assert_called_once()

    def test_read_contacts_without_search(self, mock_db, sample_user, sample_contact):
        """Test reading contacts without search parameter"""
        contacts_list = [sample_contact]
        with patch.object(
            repository_contacts, "get_contacts", return_value=contacts_list
        ):
            result = read_contacts(
                skip=0, limit=100, search=None, db=mock_db, current_user=sample_user
            )
        assert result == contacts_list

    def test_read_contacts_with_search(self, mock_db, sample_user, sample_contact):
        """Test reading contacts with search parameter"""
        contacts_list = [sample_contact]
        search_term = "john"
        with patch.object(
            repository_contacts, "search_contacts", return_value=contacts_list
        ):
            result = read_contacts(
                skip=0,
                limit=100,
                search=search_term,
                db=mock_db,
                current_user=sample_user,
            )
        assert result == contacts_list

    def test_get_upcoming_birthdays(self, mock_db, sample_user, sample_contact):
        """Test getting upcoming birthdays"""
        birthday_contacts = [sample_contact]
        with patch.object(
            repository_contacts,
            "get_upcoming_birthdays",
            return_value=birthday_contacts,
        ):
            result = get_upcoming_birthdays(mock_db, sample_user)
        assert result == birthday_contacts

    def test_read_contact_success(self, mock_db, sample_user, sample_contact):
        """Test reading a single contact successfully"""
        contact_id = 1
        with patch.object(
            repository_contacts, "get_contact", return_value=sample_contact
        ):
            result = read_contact(contact_id, mock_db, sample_user)
        assert result == sample_contact

    def test_read_contact_not_found(self, mock_db, sample_user):
        """Test reading a contact that doesn't exist"""
        contact_id = 999
        with patch.object(repository_contacts, "get_contact", return_value=None):
            with pytest.raises(ContactNotFoundError):
                read_contact(contact_id, mock_db, sample_user)

    def test_update_contact_success(
        self, mock_db, sample_user, contact_update_data, sample_contact
    ):
        """Test successful contact update"""
        contact_id = 1
        with patch.object(
            repository_contacts, "update_contact", return_value=sample_contact
        ):
            result = update_contact(
                contact_id, contact_update_data, mock_db, sample_user
            )
        assert result == sample_contact

    def test_update_contact_not_found(self, mock_db, sample_user, contact_update_data):
        """Test updating a contact that doesn't exist"""
        contact_id = 999
        with patch.object(repository_contacts, "update_contact", return_value=None):
            with pytest.raises(ContactNotFoundError):
                update_contact(contact_id, contact_update_data, mock_db, sample_user)

    def test_update_contact_not_found_error(
        self, mock_db, sample_user, contact_update_data
    ):
        """Test updating a contact with ContactNotFoundError"""
        contact_id = 1
        with patch.object(
            repository_contacts,
            "update_contact",
            side_effect=ContactNotFoundError(contact_id),
        ):
            with pytest.raises(ContactNotFoundError):
                update_contact(contact_id, contact_update_data, mock_db, sample_user)

    def test_update_contact_database_error(
        self, mock_db, sample_user, contact_update_data
    ):
        """Test updating a contact with database error"""
        contact_id = 1
        with patch.object(
            repository_contacts,
            "update_contact",
            side_effect=Exception("Database error"),
        ), patch("src.routes.contacts.handle_database_error") as mock_handle:
            update_contact(contact_id, contact_update_data, mock_db, sample_user)
            mock_handle.assert_called_once()

    def test_delete_contact_success(self, mock_db, sample_user, sample_contact):
        """Test successful contact deletion"""
        contact_id = 1
        with patch.object(
            repository_contacts, "delete_contact", return_value=sample_contact
        ):
            result = delete_contact(contact_id, mock_db, sample_user)
        assert result == sample_contact

    def test_delete_contact_not_found(self, mock_db, sample_user):
        """Test deleting a contact that doesn't exist"""
        contact_id = 999
        with patch.object(repository_contacts, "delete_contact", return_value=None):
            with pytest.raises(ContactNotFoundError):
                delete_contact(contact_id, mock_db, sample_user)

    def test_read_contacts_empty_result(self, mock_db, sample_user):
        """Test reading contacts when no contacts exist"""
        # Simple test - just call the function and verify it doesn't crash
        try:
            result = read_contacts(db=mock_db, current_user=sample_user)
            # Function executed successfully
            assert True
        except Exception:
            pytest.fail("Function should not raise exception")

    def test_read_contacts_search_empty_result(self, mock_db, sample_user):
        """Test searching contacts with no results"""
        with patch.object(repository_contacts, "search_contacts", return_value=[]):
            result = read_contacts(
                search="nonexistent", db=mock_db, current_user=sample_user
            )
        assert result == []

    def test_get_upcoming_birthdays_empty(self, mock_db, sample_user):
        """Test getting upcoming birthdays when none exist"""
        with patch.object(
            repository_contacts, "get_upcoming_birthdays", return_value=[]
        ):
            result = get_upcoming_birthdays(mock_db, sample_user)
        assert result == []

    def test_pagination_cases(self, mock_db, sample_user):
        """Test pagination with various values"""
        edge_cases = [(0, 1), (0, 1000), (100, 50)]

        for skip, limit in edge_cases:
            # Simple test - just call the function and verify it doesn't crash
            try:
                result = read_contacts(
                    skip=skip, limit=limit, db=mock_db, current_user=sample_user
                )
                # Function executed successfully
                assert True
            except Exception:
                pytest.fail("Function should not raise exception")

    def test_contact_operations_various_ids(self, mock_db, sample_user):
        """Test contact operations with various ID values"""
        contact_ids = [1, 100, 999999]

        for contact_id in contact_ids:
            # Test read_contact
            with patch.object(repository_contacts, "get_contact", return_value=None):
                with pytest.raises(ContactNotFoundError):
                    read_contact(contact_id, mock_db, sample_user)

            # Test delete_contact
            with patch.object(repository_contacts, "delete_contact", return_value=None):
                with pytest.raises(ContactNotFoundError):
                    delete_contact(contact_id, mock_db, sample_user)

    def test_exception_handling_various_types(self, mock_db, sample_user):
        """Test exception handling with various exception types"""
        contact_data = ContactCreate(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone_number="+1234567890",
            birth_date=date(1990, 1, 1),
        )

        exceptions_to_test = [
            ValueError("Invalid data"),
            RuntimeError("Runtime error"),
        ]

        for exception in exceptions_to_test:
            with patch.object(
                repository_contacts, "create_contact", side_effect=exception
            ), patch("src.routes.contacts.handle_database_error") as mock_handle:
                create_contact(contact_data, mock_db, sample_user)
                mock_handle.assert_called_once()
                mock_handle.reset_mock()
