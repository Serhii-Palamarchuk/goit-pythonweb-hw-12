"""
Tests for refresh token functionality.

This module contains tests for JWT refresh token mechanisms including
creation, validation, and refresh endpoint functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from src.services.auth import (
    create_refresh_token,
    get_refresh_token_data,
    create_access_token,
)
from src.database.models import User, UserRole


class TestRefreshTokens:
    """Test cases for refresh token functionality."""

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        data = {"sub": "test@example.com"}
        refresh_token = create_refresh_token(data)

        assert refresh_token is not None
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 50  # JWT tokens are long strings

    def test_validate_refresh_token_success(self):
        """Test successful refresh token validation."""
        data = {"sub": "test@example.com"}
        refresh_token = create_refresh_token(data)

        token_data = get_refresh_token_data(refresh_token)

        assert token_data is not None
        assert token_data["sub"] == "test@example.com"

    def test_validate_refresh_token_invalid(self):
        """Test validation of invalid refresh token."""
        invalid_token = "invalid.token.here"

        with pytest.raises(HTTPException) as exc_info:
            get_refresh_token_data(invalid_token)

        assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Invalid token" in exc_info.value.detail

    def test_validate_access_token_as_refresh(self):
        """Test that access token cannot be used as refresh token."""
        # Create access token instead of refresh token
        data = {"sub": "test@example.com"}
        access_token = create_access_token(data)

        with pytest.raises(HTTPException) as exc_info:
            get_refresh_token_data(access_token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid scope for token" in exc_info.value.detail

    def test_refresh_token_different_from_access_token(self):
        """Test that refresh and access tokens are different."""
        data = {"sub": "test@example.com"}

        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)

        assert access_token != refresh_token
        assert len(access_token) > 50
        assert len(refresh_token) > 50

    def test_refresh_token_longer_expiry(self):
        """Test that refresh token has longer expiry than access token."""
        import jwt
        from src.config import settings

        data = {"sub": "test@example.com"}

        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)

        # Decode tokens to check expiry
        access_payload = jwt.decode(
            access_token, settings.secret_key, algorithms=[settings.algorithm]
        )
        refresh_payload = jwt.decode(
            refresh_token, settings.secret_key, algorithms=[settings.algorithm]
        )

        # Refresh token should expire later than access token
        assert refresh_payload["exp"] > access_payload["exp"]

        # Refresh token should have 7 days expiry (approximately)
        refresh_exp = datetime.fromtimestamp(refresh_payload["exp"])
        refresh_iat = datetime.fromtimestamp(refresh_payload["iat"])
        expiry_duration = refresh_exp - refresh_iat

        # Should be approximately 7 days (allow some variance for test execution time)
        assert 6.9 <= expiry_duration.days <= 7.1


class TestRefreshTokenEndpoint:
    """Test cases for refresh token API endpoint."""

    def test_token_schema_includes_refresh_token(self):
        """Test that Token schema includes refresh_token field."""
        from src.schemas.users import Token

        # Check if refresh_token field exists in schema
        schema = Token.model_json_schema()
        properties = schema.get("properties", {})

        assert "access_token" in properties
        assert "refresh_token" in properties
        assert "token_type" in properties

    def test_refresh_token_request_schema(self):
        """Test RefreshTokenRequest schema."""
        from src.schemas.users import RefreshTokenRequest

        # Test valid request
        request_data = {"refresh_token": "valid.token.here"}
        request = RefreshTokenRequest(**request_data)

        assert request.refresh_token == "valid.token.here"

    def test_login_returns_both_tokens(self):
        """Test that login endpoint schema supports both tokens."""
        from src.schemas.users import Token

        # Create sample token response
        token_response = Token(
            access_token="access.token.here",
            refresh_token="refresh.token.here",
            token_type="bearer",
        )

        assert token_response.access_token == "access.token.here"
        assert token_response.refresh_token == "refresh.token.here"
        assert token_response.token_type == "bearer"


if __name__ == "__main__":
    pytest.main([__file__])
