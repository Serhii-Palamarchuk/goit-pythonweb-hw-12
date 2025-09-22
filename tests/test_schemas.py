"""Tests for Pydantic schemas."""

from datetime import date, datetime
import pytest
from pydantic import ValidationError

from src.schemas.contacts import (
    ContactBase,
    ContactCreate,
    ContactUpdate,
    ContactResponse,
)
from src.schemas.users import UserCreate, UserResponse, Token, TokenData


class TestContactSchemas:
    """Test contact-related Pydantic schemas."""

    def test_contact_base_valid_data(self):
        """Test ContactBase with valid data."""
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+1234567890",
            "birth_date": date(1990, 1, 1),
            "additional_data": "Some additional info",
        }

        contact = ContactBase(**valid_data)

        assert contact.first_name == "John"
        assert contact.last_name == "Doe"
        assert contact.email == "john.doe@example.com"
        assert contact.phone_number == "+1234567890"
        assert contact.birth_date == date(1990, 1, 1)
        assert contact.additional_data == "Some additional info"

    def test_contact_base_minimal_data(self):
        """Test ContactBase with minimal required data."""
        minimal_data = {
            "first_name": "J",
            "last_name": "D",
            "email": "j@d.com",
            "phone_number": "1",
            "birth_date": date(2000, 12, 31),
        }

        contact = ContactBase(**minimal_data)

        assert contact.first_name == "J"
        assert contact.additional_data is None

    def test_contact_base_invalid_email(self):
        """Test ContactBase with invalid email format."""
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email",
            "phone_number": "+1234567890",
            "birth_date": date(1990, 1, 1),
        }

        with pytest.raises(ValidationError) as exc_info:
            ContactBase(**invalid_data)

        assert "Invalid email format" in str(exc_info.value)

    def test_contact_base_empty_first_name(self):
        """Test ContactBase with empty first name."""
        invalid_data = {
            "first_name": "",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+1234567890",
            "birth_date": date(1990, 1, 1),
        }

        with pytest.raises(ValidationError):
            ContactBase(**invalid_data)

    def test_contact_base_long_names(self):
        """Test ContactBase with names exceeding max length."""
        invalid_data = {
            "first_name": "A" * 51,  # Too long
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+1234567890",
            "birth_date": date(1990, 1, 1),
        }

        with pytest.raises(ValidationError):
            ContactBase(**invalid_data)

    def test_contact_base_future_birth_date(self):
        """Test ContactBase with future birth date."""
        future_date = date(2030, 1, 1)
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+1234567890",
            "birth_date": future_date,
        }

        # Should be valid (business logic validation would be separate)
        contact = ContactBase(**data)
        assert contact.birth_date == future_date

    def test_contact_create_inheritance(self):
        """Test that ContactCreate inherits from ContactBase."""
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone_number": "+1987654321",
            "birth_date": date(1985, 5, 15),
        }

        contact = ContactCreate(**data)

        assert isinstance(contact, ContactBase)
        assert contact.first_name == "Jane"

    def test_contact_update_optional_fields(self):
        """Test ContactUpdate with optional fields."""
        # Should work with no fields
        update_empty = ContactUpdate()
        assert update_empty.first_name is None
        assert update_empty.last_name is None

        # Should work with some fields
        update_partial = ContactUpdate(
            first_name="UpdatedName", email="updated@example.com"
        )
        assert update_partial.first_name == "UpdatedName"
        assert update_partial.email == "updated@example.com"
        assert update_partial.last_name is None

    def test_contact_update_invalid_email(self):
        """Test ContactUpdate with invalid email."""
        with pytest.raises(ValidationError):
            ContactUpdate(email="invalid-email-format")

    def test_email_validation_edge_cases(self):
        """Test email validation with various edge cases."""
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "user+tag@example.org",
            "1234567890@domain.com",
            "user_name@domain-name.com",
        ]

        for email in valid_emails:
            data = {
                "first_name": "Test",
                "last_name": "User",
                "email": email,
                "phone_number": "123456789",
                "birth_date": date(1990, 1, 1),
            }
            contact = ContactBase(**data)
            assert contact.email == email

        invalid_emails = [
            "user@",
            "@domain.com",
            "user.domain.com",
            "user@domain",
            "",
            "user@@domain.com",
        ]

        for email in invalid_emails:
            data = {
                "first_name": "Test",
                "last_name": "User",
                "email": email,
                "phone_number": "123456789",
                "birth_date": date(1990, 1, 1),
            }
            with pytest.raises(ValidationError):
                ContactBase(**data)


class TestUserSchemas:
    """Test user-related Pydantic schemas."""

    def test_user_create_valid_data(self):
        """Test UserCreate with valid data."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
        }

        user = UserCreate(**user_data)

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "securepassword123"

    def test_user_create_email_validation(self):
        """Test UserCreate email validation."""
        invalid_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "securepassword123",
        }

        with pytest.raises(ValidationError):
            UserCreate(**invalid_data)

    def test_token_schema(self):
        """Test Token schema."""
        token_data = {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "token_type": "bearer",
        }

        token = Token(**token_data)

        assert token.access_token == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        assert token.token_type == "bearer"

    def test_token_data_schema(self):
        """Test TokenData schema."""
        # Should work with username
        token_data = TokenData(username="testuser")
        assert token_data.username == "testuser"

        # Should work with None
        token_data_none = TokenData(username=None)
        assert token_data_none.username is None

    def test_schema_serialization(self):
        """Test that schemas can be serialized to dict."""
        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone_number": "+1234567890",
            "birth_date": date(1990, 1, 1),
        }

        contact = ContactCreate(**contact_data)
        contact_dict = contact.dict()

        assert isinstance(contact_dict, dict)
        assert contact_dict["first_name"] == "John"
        assert contact_dict["birth_date"] == date(1990, 1, 1)

    def test_schema_json_serialization(self):
        """Test that schemas can be serialized to JSON."""
        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone_number": "+1234567890",
            "birth_date": date(1990, 1, 1),
        }

        contact = ContactCreate(**contact_data)
        contact_json = contact.json()

        assert isinstance(contact_json, str)
        assert "John" in contact_json
        assert "1990-01-01" in contact_json
