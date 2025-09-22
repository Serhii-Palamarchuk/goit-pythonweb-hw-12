import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
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


class TestContactRoutes:
    """Test contact route handlers directly"""

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
        from datetime import date

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
        repository_contacts.create_contact.assert_called_once_with(
            db=mock_db, contact=contact_create_data, user=sample_user
        )

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
        ), patch("src.routes.contacts.handle_database_error") as mock_handle_error:

            create_contact(contact_create_data, mock_db, sample_user)
            mock_handle_error.assert_called_once()

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
        repository_contacts.get_contacts.assert_called_once_with(
            mock_db, sample_user, skip=0, limit=100
        )

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
        repository_contacts.search_contacts.assert_called_once_with(
            mock_db, sample_user, search_term
        )

    def test_read_contacts_custom_pagination(
        self, mock_db, sample_user, sample_contact
    ):
        """Test reading contacts with custom pagination"""
        contacts_list = [sample_contact]

        with patch.object(
            repository_contacts, "get_contacts", return_value=contacts_list
        ):
            result = read_contacts(
                skip=10, limit=50, search=None, db=mock_db, current_user=sample_user
            )

        assert result == contacts_list
        repository_contacts.get_contacts.assert_called_once_with(
            mock_db, sample_user, skip=10, limit=50
        )

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
        repository_contacts.get_upcoming_birthdays.assert_called_once_with(
            mock_db, sample_user
        )

    def test_read_contact_success(self, mock_db, sample_user, sample_contact):
        """Test reading a single contact successfully"""
        contact_id = 1

        with patch.object(
            repository_contacts, "get_contact", return_value=sample_contact
        ):
            result = read_contact(contact_id, mock_db, sample_user)

        assert result == sample_contact
        repository_contacts.get_contact.assert_called_once_with(
            mock_db, contact_id=contact_id, user=sample_user
        )

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
        repository_contacts.update_contact.assert_called_once_with(
            mock_db,
            contact_id=contact_id,
            contact=contact_update_data,
            user=sample_user,
        )

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
        ), patch("src.routes.contacts.handle_database_error") as mock_handle_error:

            update_contact(contact_id, contact_update_data, mock_db, sample_user)
            mock_handle_error.assert_called_once()

    def test_delete_contact_success(self, mock_db, sample_user, sample_contact):
        """Test successful contact deletion"""
        contact_id = 1

        with patch.object(
            repository_contacts, "delete_contact", return_value=sample_contact
        ):
            result = delete_contact(contact_id, mock_db, sample_user)

        assert result == sample_contact
        repository_contacts.delete_contact.assert_called_once_with(
            mock_db, contact_id=contact_id, user=sample_user
        )

    def test_delete_contact_not_found(self, mock_db, sample_user):
        """Test deleting a contact that doesn't exist"""
        contact_id = 999

        with patch.object(repository_contacts, "delete_contact", return_value=None):
            with pytest.raises(ContactNotFoundError):
                delete_contact(contact_id, mock_db, sample_user)


class TestContactRoutesEdgeCases:
    """Test edge cases and parameter variations"""

    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)

    @pytest.fixture
    def sample_user(self):
        user = Mock(spec=User)
        user.id = 1
        user.username = "testuser"
        return user

    def test_read_contacts_empty_result(self, mock_db, sample_user):
        """Test reading contacts when no contacts exist"""
        with patch.object(repository_contacts, "get_contacts", return_value=[]):
            result = read_contacts(db=mock_db, current_user=sample_user)

        assert result == []

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

    def test_read_contacts_various_search_terms(self, mock_db, sample_user):
        """Test reading contacts with various search terms"""
        search_terms = ["john", "doe", "john.doe@example.com", "+1234", ""]

        for search_term in search_terms:
            with patch.object(
                repository_contacts, "search_contacts", return_value=[]
            ) as mock_search:
                result = read_contacts(
                    search=search_term, db=mock_db, current_user=sample_user
                )

                if search_term:  # Only call search_contacts for non-empty search terms
                    mock_search.assert_called_once_with(
                        mock_db, sample_user, search_term
                    )
                else:
                    # Empty string should not trigger search
                    with patch.object(
                        repository_contacts, "get_contacts", return_value=[]
                    ):
                        read_contacts(search="", db=mock_db, current_user=sample_user)

    def test_pagination_edge_cases(self, mock_db, sample_user):
        """Test pagination with edge case values"""
        edge_cases = [
            (0, 1),  # Minimum limit
            (0, 1000),  # Large limit
            (100, 50),  # Skip more than limit
        ]

        for skip, limit in edge_cases:
            with patch.object(repository_contacts, "get_contacts", return_value=[]):
                result = read_contacts(
                    skip=skip, limit=limit, db=mock_db, current_user=sample_user
                )
                assert result == []

    def test_contact_operations_with_different_ids(self, mock_db, sample_user):
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

    def test_repository_function_calls(self, mock_db, sample_user):
        """Test that repository functions are called with correct parameters"""
        # Test create_contact
        from datetime import date

        contact_data = ContactCreate(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone_number="+1234567890",
            birth_date=date(1990, 1, 1),
        )

        with patch.object(
            repository_contacts, "create_contact", return_value=Mock()
        ) as mock_create:
            create_contact(contact_data, mock_db, sample_user)

            call_args = mock_create.call_args
            assert call_args[1]["db"] == mock_db
            assert call_args[1]["contact"] == contact_data
            assert call_args[1]["user"] == sample_user

        # Test get_contacts
        with patch.object(
            repository_contacts, "get_contacts", return_value=[]
        ) as mock_get:
            read_contacts(skip=5, limit=10, db=mock_db, current_user=sample_user)

            call_args = mock_get.call_args
            assert call_args[0][0] == mock_db  # First positional arg
            assert call_args[0][1] == sample_user  # Second positional arg
            assert call_args[1]["skip"] == 5
            assert call_args[1]["limit"] == 10


class TestContactRoutesExceptionHandling:
    """Test exception handling scenarios"""

    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)

    @pytest.fixture
    def sample_user(self):
        return Mock(spec=User)

    def test_create_contact_various_exceptions(self, mock_db, sample_user):
        """Test create_contact with various exception types"""
        from datetime import date

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
            AttributeError("Attribute error"),
        ]

        for exception in exceptions_to_test:
            with patch.object(
                repository_contacts, "create_contact", side_effect=exception
            ), patch("src.routes.contacts.handle_database_error") as mock_handle:

                create_contact(contact_data, mock_db, sample_user)
                mock_handle.assert_called_once_with(exception, "створення контакту")
                mock_handle.reset_mock()

    def test_update_contact_various_exceptions(self, mock_db, sample_user):
        """Test update_contact with various exception types"""
        contact_data = ContactUpdate(first_name="Updated")
        contact_id = 1

        exceptions_to_test = [
            ValueError("Invalid data"),
            RuntimeError("Runtime error"),
        ]

        for exception in exceptions_to_test:
            with patch.object(
                repository_contacts, "update_contact", side_effect=exception
            ), patch("src.routes.contacts.handle_database_error") as mock_handle:

                update_contact(contact_id, contact_data, mock_db, sample_user)
                mock_handle.assert_called_once_with(exception, "оновлення контакту")
                mock_handle.reset_mock()

    def test_contact_not_found_error_propagation(self, mock_db, sample_user):
        """Test that ContactNotFoundError is properly propagated"""
        contact_id = 1
        contact_data = ContactUpdate(first_name="Updated")

        # Test in create_contact
        with patch.object(
            repository_contacts,
            "create_contact",
            side_effect=ContactNotFoundError(contact_id),
        ):
            with pytest.raises(ContactNotFoundError) as exc_info:
                from datetime import date

                test_contact = ContactCreate(
                    first_name="Test",
                    last_name="User",
                    email="test@example.com",
                    phone_number="+1234567890",
                    birth_date=date(1990, 1, 1),
                )
                create_contact(test_contact, mock_db, sample_user)
            assert exc_info.value.contact_id == contact_id

        # Test in update_contact
        with patch.object(
            repository_contacts,
            "update_contact",
            side_effect=ContactNotFoundError(contact_id),
        ):
            with pytest.raises(ContactNotFoundError) as exc_info:
                update_contact(contact_id, contact_data, mock_db, sample_user)
            assert exc_info.value.contact_id == contact_id
