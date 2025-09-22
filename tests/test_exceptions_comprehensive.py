"""
Comprehensive tests for exceptions module.
"""

import pytest
from unittest.mock import Mock, patch
import re

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from src.exceptions import (
    ContactAPIException,
    ContactNotFoundError,
    EmailAlreadyExistsError,
    InvalidDataError,
    handle_database_error,
    handle_validation_error,
    safe_database_operation,
)


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_contact_api_exception_inheritance(self):
        """Test ContactAPIException inherits from HTTPException."""
        exception = ContactAPIException(status_code=400, detail="Test error")
        assert isinstance(exception, HTTPException)

    def test_contact_not_found_error(self):
        """Test ContactNotFoundError creation and properties."""
        contact_id = 123
        error = ContactNotFoundError(contact_id)

        assert error.status_code == status.HTTP_404_NOT_FOUND
        assert f"ID {contact_id}" in error.detail
        assert "не знайдено" in error.detail
        assert isinstance(error, ContactAPIException)

    def test_email_already_exists_error(self):
        """Test EmailAlreadyExistsError creation and properties."""
        email = "test@example.com"
        error = EmailAlreadyExistsError(email)

        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert email in error.detail
        assert "вже існує" in error.detail
        assert isinstance(error, ContactAPIException)

    def test_invalid_data_error(self):
        """Test InvalidDataError creation and properties."""
        details = "Invalid phone number format"
        error = InvalidDataError(details)

        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert details in error.detail
        assert "Некоректні дані" in error.detail
        assert isinstance(error, ContactAPIException)

    def test_exception_messages_with_special_characters(self):
        """Test exceptions handle special characters correctly."""
        # Test with email containing special characters
        email = "test+tag@sub.domain.com"
        error = EmailAlreadyExistsError(email)
        assert email in error.detail

        # Test with details containing quotes and slashes
        details = "Field 'name' contains invalid characters: /\\"
        error = InvalidDataError(details)
        assert details in error.detail

    def test_exception_inheritance_chain(self):
        """Test exception inheritance chain."""
        error = ContactNotFoundError(1)

        assert isinstance(error, ContactNotFoundError)
        assert isinstance(error, ContactAPIException)
        assert isinstance(error, HTTPException)
        assert isinstance(error, Exception)


class TestHandleDatabaseError:
    """Test handle_database_error function."""

    def test_integrity_error_duplicate_email(self):
        """Test handling duplicate email constraint violation."""
        # Mock IntegrityError with email constraint violation
        orig_error = Mock()
        orig_error.__str__ = Mock(
            return_value=(
                'duplicate key value violates unique constraint "ix_contacts_email"'
                " DETAIL: Key (email)=(test@example.com) already exists."
            )
        )

        integrity_error = IntegrityError(
            "statement", "params", orig_error, "connection_invalidated"
        )
        integrity_error.orig = orig_error

        with pytest.raises(EmailAlreadyExistsError) as exc_info:
            handle_database_error(integrity_error, "створення контакту")

        assert "test@example.com" in str(exc_info.value.detail)

    def test_integrity_error_duplicate_email_without_match(self):
        """Test handling duplicate constraint without email extraction."""
        orig_error = Mock()
        orig_error.__str__ = Mock(
            return_value=(
                'duplicate key value violates unique constraint "ix_contacts_email"'
                " DETAIL: Key already exists."
            )
        )

        integrity_error = IntegrityError(
            "statement", "params", orig_error, "connection_invalidated"
        )
        integrity_error.orig = orig_error

        with pytest.raises(EmailAlreadyExistsError) as exc_info:
            handle_database_error(integrity_error, "створення контакту")

        assert "невідомий" in str(exc_info.value.detail)

    def test_integrity_error_general_duplicate(self):
        """Test handling general duplicate key constraint violation."""
        orig_error = Mock()
        orig_error.__str__ = Mock(
            return_value=(
                'duplicate key value violates unique constraint "ix_contacts_username"'
                " DETAIL: Key (username)=(testuser) already exists."
            )
        )

        integrity_error = IntegrityError(
            "statement", "params", orig_error, "connection_invalidated"
        )
        integrity_error.orig = orig_error

        with pytest.raises(InvalidDataError) as exc_info:
            handle_database_error(integrity_error, "створення користувача")

        assert "Дублювання унікального значення" in str(exc_info.value.detail)

    def test_integrity_error_foreign_key_constraint(self):
        """Test handling foreign key constraint violation."""
        orig_error = Mock()
        orig_error.__str__ = Mock(
            return_value=(
                'insert or update on table "contacts" violates foreign key constraint'
            )
        )

        integrity_error = IntegrityError(
            "statement", "params", orig_error, "connection_invalidated"
        )
        integrity_error.orig = orig_error

        with pytest.raises(InvalidDataError) as exc_info:
            handle_database_error(integrity_error, "оновлення контакту")

        assert "Порушення зв'язку" in str(exc_info.value.detail)

    def test_integrity_error_not_null_constraint(self):
        """Test handling not-null constraint violation."""
        orig_error = Mock()
        orig_error.__str__ = Mock(
            return_value=(
                'null value in column "first_name" violates not-null constraint'
            )
        )

        integrity_error = IntegrityError(
            "statement", "params", orig_error, "connection_invalidated"
        )
        integrity_error.orig = orig_error

        with pytest.raises(InvalidDataError) as exc_info:
            handle_database_error(integrity_error, "створення контакту")

        assert "first_name" in str(exc_info.value.detail)
        assert "не може бути пустим" in str(exc_info.value.detail)

    def test_integrity_error_not_null_constraint_no_field_match(self):
        """Test handling not-null constraint without field extraction."""
        orig_error = Mock()
        orig_error.__str__ = Mock(
            return_value=("null value violates not-null constraint")
        )

        integrity_error = IntegrityError(
            "statement", "params", orig_error, "connection_invalidated"
        )
        integrity_error.orig = orig_error

        with pytest.raises(InvalidDataError) as exc_info:
            handle_database_error(integrity_error, "створення контакту")

        assert "невідоме поле" in str(exc_info.value.detail)

    def test_integrity_error_unknown_type(self):
        """Test handling unknown IntegrityError type."""
        orig_error = Mock()
        orig_error.__str__ = Mock(return_value="Some unknown integrity error")

        integrity_error = IntegrityError(
            "statement", "params", orig_error, "connection_invalidated"
        )
        integrity_error.orig = orig_error

        with pytest.raises(HTTPException) as exc_info:
            handle_database_error(integrity_error, "операції з базою")

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Помилка цілісності даних" in exc_info.value.detail

    @patch("src.exceptions.logger")
    def test_general_database_error(self, mock_logger):
        """Test handling general database errors."""
        error = Exception("Database connection failed")

        with pytest.raises(HTTPException) as exc_info:
            handle_database_error(error, "з'єднання з базою")

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Внутрішня помилка сервера" in exc_info.value.detail
        mock_logger.error.assert_called_once()

    def test_handle_database_error_default_operation(self):
        """Test handle_database_error with default operation parameter."""
        error = Exception("Generic error")

        with pytest.raises(HTTPException):
            handle_database_error(error)


class TestHandleValidationError:
    """Test handle_validation_error function."""

    def test_single_validation_error(self):
        """Test handling single validation error."""
        # Create mock ValidationError
        error_dict = {
            "loc": ("email",),
            "msg": "field required",
            "type": "value_error.missing",
        }

        # Mock ValidationError
        validation_error = Mock(spec=ValidationError)
        validation_error.errors.return_value = [error_dict]

        with pytest.raises(HTTPException) as exc_info:
            handle_validation_error(validation_error)

        assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "email: field required" in exc_info.value.detail
        assert "Помилки валідації" in exc_info.value.detail

    def test_multiple_validation_errors(self):
        """Test handling multiple validation errors."""
        errors_list = [
            {"loc": ("email",), "msg": "field required", "type": "value_error.missing"},
            {
                "loc": ("first_name",),
                "msg": "ensure this value has at least 1 characters",
                "type": "value_error.any_str.min_length",
            },
            {
                "loc": ("contacts", 0, "phone"),
                "msg": "invalid phone number format",
                "type": "value_error.str.regex",
            },
        ]

        validation_error = Mock(spec=ValidationError)
        validation_error.errors.return_value = errors_list

        with pytest.raises(HTTPException) as exc_info:
            handle_validation_error(validation_error)

        detail = exc_info.value.detail
        assert "email: field required" in detail
        assert "first_name: ensure this value" in detail
        assert "contacts -> 0 -> phone: invalid phone" in detail
        assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_nested_field_validation_error(self):
        """Test handling validation error with nested field location."""
        error_dict = {
            "loc": ("user", "profile", "settings", "theme"),
            "msg": "must be one of: light, dark",
            "type": "value_error.choices",
        }

        validation_error = Mock(spec=ValidationError)
        validation_error.errors.return_value = [error_dict]

        with pytest.raises(HTTPException) as exc_info:
            handle_validation_error(validation_error)

        assert "user -> profile -> settings -> theme" in exc_info.value.detail


class TestSafeDatabaseOperation:
    """Test safe_database_operation decorator."""

    def test_successful_operation(self):
        """Test decorator with successful operation."""

        @safe_database_operation
        def successful_func(x, y):
            return x + y

        result = successful_func(2, 3)
        assert result == 5

    def test_operation_with_integrity_error(self):
        """Test decorator handling IntegrityError."""
        orig_error = Mock()
        orig_error.__str__ = Mock(
            return_value=(
                'duplicate key value violates unique constraint "ix_contacts_email"'
                " DETAIL: Key (email)=(test@example.com) already exists."
            )
        )

        integrity_error = IntegrityError(
            "statement", "params", orig_error, "connection_invalidated"
        )
        integrity_error.orig = orig_error

        @safe_database_operation
        def failing_func():
            raise integrity_error

        with pytest.raises(EmailAlreadyExistsError):
            failing_func()

    def test_operation_with_general_exception(self):
        """Test decorator handling general exception."""

        @safe_database_operation
        def failing_func():
            raise Exception("Database connection failed")

        with pytest.raises(HTTPException) as exc_info:
            failing_func()

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_operation_with_custom_operation_name(self):
        """Test decorator with custom operation name."""

        def custom_operation_func():
            raise Exception("Test error")

        decorated_func = safe_database_operation(
            custom_operation_func, "кастомна операція"
        )

        with pytest.raises(HTTPException):
            decorated_func()

    def test_decorator_preserves_function_signature(self):
        """Test that decorator preserves original function signature."""

        @safe_database_operation
        def complex_func(a, b, c=None, *args, **kwargs):
            return {"a": a, "b": b, "c": c, "args": args, "kwargs": kwargs}

        result = complex_func(1, 2, c=3, extra=4)
        expected = {"a": 1, "b": 2, "c": 3, "args": (), "kwargs": {"extra": 4}}
        assert result == expected


class TestExceptionsIntegration:
    """Test integration scenarios with exceptions."""

    def test_regex_patterns_work_correctly(self):
        """Test that regex patterns correctly extract information."""
        # Test email extraction
        error_msg = "Key (email)=(user+tag@domain.co.uk) already exists"
        email_match = re.search(r"\(email\)=\(([^)]+)\)", error_msg)
        assert email_match is not None
        assert email_match.group(1) == "user+tag@domain.co.uk"

        # Test field extraction for not-null
        error_msg = 'null value in column "complex_field_name" violates'
        field_match = re.search(r'column "([^"]+)"', error_msg)
        assert field_match is not None
        assert field_match.group(1) == "complex_field_name"

    def test_exception_details_are_informative(self):
        """Test that exception details provide useful information."""
        # Test ContactNotFoundError
        error = ContactNotFoundError(999)
        assert "999" in error.detail
        assert "ID" in error.detail

        # Test EmailAlreadyExistsError
        error = EmailAlreadyExistsError("very.long.email@subdomain.example.org")
        assert "very.long.email@subdomain.example.org" in error.detail
        assert "Використайте інший email" in error.detail

        # Test InvalidDataError
        error = InvalidDataError(
            "Phone number must contain only digits and + - ( ) characters"
        )
        assert "Phone number must contain only digits" in error.detail

    def test_status_codes_are_correct(self):
        """Test that all custom exceptions have correct status codes."""
        assert ContactNotFoundError(1).status_code == 404
        assert EmailAlreadyExistsError("test@test.com").status_code == 400
        assert InvalidDataError("test").status_code == 400

    def test_all_exceptions_are_serializable(self):
        """Test that exceptions can be properly serialized for HTTP responses."""
        exceptions = [
            ContactNotFoundError(123),
            EmailAlreadyExistsError("test@example.com"),
            InvalidDataError("Test details"),
        ]

        for exc in exceptions:
            # Should be able to access these properties without errors
            assert isinstance(exc.status_code, int)
            assert isinstance(exc.detail, str)
            assert len(exc.detail) > 0
