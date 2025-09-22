"""Tests for authentication service."""

from datetime import datetime, timedelta
import pytest
from jose import jwt

import src.services.auth as auth_service
from src.config import settings


class TestAuthFunctions:
    """Test authentication service functions."""

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        plain_password = "testpassword123"
        hashed_password = auth_service.get_password_hash(plain_password)

        result = auth_service.verify_password(plain_password, hashed_password)

        assert result is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        plain_password = "testpassword123"
        wrong_password = "wrongpassword456"
        hashed_password = auth_service.get_password_hash(plain_password)

        result = auth_service.verify_password(wrong_password, hashed_password)

        assert result is False

    def test_verify_password_empty_strings(self):
        """Test password verification with empty strings."""
        result = auth_service.verify_password("", "")

        assert result is False

    def test_get_password_hash_generates_different_hashes(self):
        """Test that same password generates different hashes each time."""
        password = "testpassword123"

        hash1 = auth_service.get_password_hash(password)
        hash2 = auth_service.get_password_hash(password)

        assert hash1 != hash2
        assert len(hash1) > 50  # bcrypt hashes are long
        assert hash1.startswith("$2b$")
        assert len(hash2) > 50
        assert hash2.startswith("$2b$")

    def test_get_password_hash_unicode_password(self):
        """Test password hashing with unicode characters."""
        password = "тестовий_пароль_123"

        hashed = auth_service.get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 50
        assert auth_service.verify_password(password, hashed)

    def test_create_access_token_default_expiry(self):
        """Test access token creation with default expiry."""
        data = {"sub": "test@example.com", "user_id": 1}

        token = auth_service.create_access_token(data)

        # Decode token to verify payload
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert "exp" in payload

        # Verify expiry is approximately default time from now
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_time = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        time_diff = abs((exp_time - expected_time).total_seconds())
        assert time_diff < 10  # Allow 10 seconds difference

    def test_create_access_token_custom_expiry(self):
        """Test access token creation with custom expiry."""
        data = {"sub": "test@example.com", "user_id": 1}
        expires_delta = timedelta(minutes=5)

        token = auth_service.create_access_token(data, expires_delta)

        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["sub"] == "test@example.com"

        # Check expiry is approximately 5 minutes from now
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_time = datetime.utcnow() + expires_delta
        time_diff = abs((exp_time - expected_time).total_seconds())
        assert time_diff < 10  # Allow 10 seconds difference

    def test_create_access_token_empty_data(self):
        """Test access token creation with empty data."""
        data = {}

        token = auth_service.create_access_token(data)

        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert "exp" in payload
        # Should only contain expiry

    def test_create_access_token_with_additional_claims(self):
        """Test access token creation with additional claims."""
        data = {
            "sub": "test@example.com",
            "user_id": 1,
            "role": "admin",
            "permissions": ["read", "write"],
        }

        token = auth_service.create_access_token(data)

        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]

    def test_create_access_token_zero_expiry(self):
        """Test access token creation with zero expiry."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(seconds=0)

        token = auth_service.create_access_token(data, expires_delta)

        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        # Token should be already expired or expire very soon
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        assert exp_time <= now + timedelta(seconds=1)

    def test_multiple_password_operations(self):
        """Test multiple password operations for consistency."""
        passwords = [
            "simple123",
            "Complex_Password!@#123",
            "очень_сложный_пароль_2023",
            "🔒secure🔑password🛡️",
            "a" * 100,  # Long password
        ]

        for password in passwords:
            # Hash password
            hashed = auth_service.get_password_hash(password)

            # Verify correct password
            assert auth_service.verify_password(password, hashed) is True

            # Verify incorrect password
            assert auth_service.verify_password(password + "wrong", hashed) is False

            # Check hash properties
            assert len(hashed) > 50
            assert hashed.startswith("$2b$")

    def test_token_can_be_decoded(self):
        """Test that created tokens can be properly decoded."""
        test_data = {"sub": "user@test.com", "role": "user", "exp_test": True}

        token = auth_service.create_access_token(test_data)

        # Should be able to decode without errors
        decoded = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        assert decoded["sub"] == "user@test.com"
        assert decoded["role"] == "user"
        assert decoded["exp_test"] is True
        assert "exp" in decoded
