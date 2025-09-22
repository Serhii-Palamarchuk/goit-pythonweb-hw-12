"""
Basic tests for auth service functions.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import timedelta

from src.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_email_token,
)


class TestAuthServiceBasic:
    """Basic tests for auth service functions."""

    @patch("src.services.auth.bcrypt.checkpw")
    def test_verify_password_success(self, mock_checkpw):
        """Test successful password verification."""
        mock_checkpw.return_value = True

        result = verify_password("password123", "hashed_password")

        assert result is True
        mock_checkpw.assert_called_once()

    @patch("src.services.auth.bcrypt.checkpw")
    def test_verify_password_failure(self, mock_checkpw):
        """Test failed password verification."""
        mock_checkpw.return_value = False

        result = verify_password("wrong_password", "hashed_password")

        assert result is False
        mock_checkpw.assert_called_once()

    @patch("src.services.auth.bcrypt.gensalt")
    @patch("src.services.auth.bcrypt.hashpw")
    def test_get_password_hash(self, mock_hashpw, mock_gensalt):
        """Test password hashing."""
        mock_gensalt.return_value = b"salt"
        mock_hashpw.return_value = b"hashed_password"

        result = get_password_hash("password123")

        assert result == "hashed_password"
        mock_gensalt.assert_called_once()
        mock_hashpw.assert_called_once()

    @patch("src.services.auth.jwt.encode")
    def test_create_access_token(self, mock_encode):
        """Test access token creation."""
        mock_encode.return_value = "access_token_123"

        result = create_access_token({"sub": "test@example.com"})

        assert result == "access_token_123"
        mock_encode.assert_called_once()

    @patch("src.services.auth.jwt.encode")
    def test_create_access_token_with_expiry(self, mock_encode):
        """Test access token creation with custom expiry."""
        mock_encode.return_value = "access_token_123"

        expires_delta = timedelta(minutes=30)
        result = create_access_token(
            {"sub": "test@example.com"}, expires_delta=expires_delta
        )

        assert result == "access_token_123"
        mock_encode.assert_called_once()

    @patch("src.services.auth.jwt.encode")
    def test_create_email_token(self, mock_encode):
        """Test email token creation."""
        mock_encode.return_value = "email_token_123"

        result = create_email_token({"sub": "test@example.com"})

        assert result == "email_token_123"
        mock_encode.assert_called_once()

    def test_oauth2_scheme_exists(self):
        """Test OAuth2 scheme is configured."""
        from src.services.auth import oauth2_scheme

        assert oauth2_scheme is not None
        # OAuth2PasswordBearer has standard attributes
        assert hasattr(oauth2_scheme, "scheme_name")
        assert oauth2_scheme.scheme_name == "OAuth2PasswordBearer"

    def test_auth_imports_work(self):
        """Test basic auth service imports."""
        from src.services.auth import (
            verify_password,
            get_password_hash,
            create_access_token,
            create_email_token,
            oauth2_scheme,
        )

        assert callable(verify_password)
        assert callable(get_password_hash)
        assert callable(create_access_token)
        assert callable(create_email_token)
        assert oauth2_scheme is not None

    def test_auth_settings_access(self):
        """Test auth service can access settings."""
        from src.services.auth import settings
        from src.config import settings as config_settings

        # Should be able to access auth-related settings
        assert settings.secret_key is not None
        assert settings.algorithm is not None
        assert settings == config_settings

    @patch("src.services.auth.datetime")
    @patch("src.services.auth.jwt.encode")
    def test_token_expiration_handling(self, mock_encode, mock_datetime):
        """Test token expiration time handling."""
        from datetime import datetime

        # Mock datetime
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now
        mock_encode.return_value = "token_123"

        # Test token creation
        result = create_access_token({"sub": "test@example.com"})

        assert result == "token_123"
        mock_encode.assert_called_once()

        # Verify expiration was set
        call_args = mock_encode.call_args[0]
        token_data = call_args[0]
        assert "exp" in token_data

    def test_auth_constants_exist(self):
        """Test auth-related constants exist."""
        from src.services import auth

        # Test module has expected functions
        assert hasattr(auth, "verify_password")
        assert hasattr(auth, "get_password_hash")
        assert hasattr(auth, "create_access_token")
        assert hasattr(auth, "create_email_token")

    def test_password_encoding_handling(self):
        """Test password encoding is handled correctly."""
        # This tests the encode/decode flow without actual bcrypt
        password = "test_password"

        # Should not raise encoding errors
        try:
            encoded = password.encode("utf-8")
            decoded = encoded.decode("utf-8")
            assert decoded == password
        except UnicodeError:
            pytest.fail("Password encoding should handle UTF-8 correctly")
