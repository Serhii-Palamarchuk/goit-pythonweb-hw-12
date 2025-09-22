"""
Simple tests for auth service advanced functions.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.services.auth import (
    get_email_from_token,
    verify_password_reset_token,
    check_admin_role,
    create_password_reset_token,
)
from src.database.models import User, UserRole


class TestAuthSimpleFunctions:
    """Test auth service functions that don't require complex mocking."""

    @pytest.mark.asyncio
    async def test_create_password_reset_token(self):
        """Test password reset token creation."""
        data = {"sub": "test@example.com"}

        with patch("src.services.auth.jwt.encode") as mock_encode:
            with patch("src.services.auth.datetime") as mock_datetime:
                # Mock datetime
                mock_now = datetime(2023, 1, 1, 12, 0, 0)
                mock_datetime.utcnow.return_value = mock_now
                mock_encode.return_value = "reset_token_123"

                result = create_password_reset_token(data)

                assert result == "reset_token_123"
                mock_encode.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_email_from_token_success(self):
        """Test successful email extraction from token."""
        token_payload = {
            "sub": "test@example.com",
            "scope": "email_token",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = token_payload

            result = await get_email_from_token("valid_email_token")

            assert result == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_email_from_token_wrong_scope(self):
        """Test get_email_from_token with wrong scope."""
        token_payload = {
            "sub": "test@example.com",
            "scope": "access_token",  # Wrong scope
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = token_payload

            with pytest.raises(HTTPException) as exc_info:
                await get_email_from_token("wrong_scope_token")

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid scope for token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_email_from_token_invalid_token(self):
        """Test get_email_from_token with invalid token."""
        from jose import JWTError

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.side_effect = JWTError("Invalid token")

            with pytest.raises(HTTPException) as exc_info:
                await get_email_from_token("invalid_token")

            assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "Invalid token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_password_reset_token_success(self):
        """Test successful password reset token verification."""
        token_payload = {
            "sub": "test@example.com",
            "scope": "password_reset",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = token_payload

            result = await verify_password_reset_token("valid_reset_token")

            assert result == "test@example.com"

    @pytest.mark.asyncio
    async def test_verify_password_reset_token_wrong_scope(self):
        """Test verify_password_reset_token with wrong scope."""
        token_payload = {
            "sub": "test@example.com",
            "scope": "email_token",  # Wrong scope
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = token_payload

            with pytest.raises(HTTPException) as exc_info:
                await verify_password_reset_token("wrong_scope_token")

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid scope for token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_password_reset_token_invalid_token(self):
        """Test verify_password_reset_token with invalid token."""
        from jose import JWTError

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.side_effect = JWTError("Invalid token")

            with pytest.raises(HTTPException) as exc_info:
                await verify_password_reset_token("invalid_token")

            assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "Invalid token" in exc_info.value.detail

    def test_check_admin_role_success(self):
        """Test check_admin_role with admin user."""
        mock_admin_user = Mock(spec=User)
        mock_admin_user.role = UserRole.ADMIN

        result = check_admin_role(mock_admin_user)

        assert result == mock_admin_user

    def test_check_admin_role_not_admin(self):
        """Test check_admin_role with non-admin user."""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.USER

        with pytest.raises(HTTPException) as exc_info:
            check_admin_role(mock_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in exc_info.value.detail

    def test_auth_module_imports(self):
        """Test that auth module functions can be imported."""
        from src.services.auth import (
            create_password_reset_token,
            get_email_from_token,
            verify_password_reset_token,
            check_admin_role,
        )

        assert callable(create_password_reset_token)
        assert callable(get_email_from_token)
        assert callable(verify_password_reset_token)
        assert callable(check_admin_role)

    def test_user_role_enum_values(self):
        """Test UserRole enum has expected values."""
        assert UserRole.USER.value == "user"
        assert UserRole.ADMIN.value == "admin"

        # Test enum comparison
        admin_role = UserRole.ADMIN
        user_role = UserRole.USER

        assert admin_role != user_role
        assert admin_role == UserRole.ADMIN

    @pytest.mark.asyncio
    async def test_token_payload_structure(self):
        """Test token payload structure handling."""
        # Test payload with missing sub
        token_payload_no_sub = {
            "scope": "email_token",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = token_payload_no_sub

            with pytest.raises(KeyError):
                await get_email_from_token("token_without_sub")

    @pytest.mark.asyncio
    async def test_scope_validation(self):
        """Test scope validation in token functions."""
        # Test different scopes
        scopes_to_test = [
            ("email_token", True, get_email_from_token),
            ("password_reset", True, verify_password_reset_token),
            ("wrong_scope", False, get_email_from_token),
            ("wrong_scope", False, verify_password_reset_token),
        ]

        for scope, should_succeed, func in scopes_to_test:
            token_payload = {
                "sub": "test@example.com",
                "scope": scope,
                "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
            }

            with patch("src.services.auth.jwt.decode") as mock_decode:
                mock_decode.return_value = token_payload

                if (
                    should_succeed
                    and scope == "email_token"
                    and func == get_email_from_token
                ):
                    result = await func("valid_token")
                    assert result == "test@example.com"
                elif (
                    should_succeed
                    and scope == "password_reset"
                    and func == verify_password_reset_token
                ):
                    result = await func("valid_token")
                    assert result == "test@example.com"
                else:
                    with pytest.raises(HTTPException) as exc_info:
                        await func("invalid_scope_token")
                    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_jwt_decode_integration(self):
        """Test JWT decode functionality is properly integrated."""
        from jose import jwt

        # This tests that the auth module can use JWT functionality
        test_payload = {"sub": "test@example.com", "scope": "test"}
        test_secret = "test_secret"
        test_algorithm = "HS256"

        # Encode a token
        token = jwt.encode(test_payload, test_secret, algorithm=test_algorithm)

        # Decode the token
        decoded = jwt.decode(token, test_secret, algorithms=[test_algorithm])

        assert decoded["sub"] == "test@example.com"
        assert decoded["scope"] == "test"

    @pytest.mark.asyncio
    async def test_exception_details_are_informative(self):
        """Test that exception messages provide useful information."""
        # Test wrong scope error
        token_payload = {
            "sub": "test@example.com",
            "scope": "wrong_scope",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = token_payload

            with pytest.raises(HTTPException) as exc_info:
                await get_email_from_token("token")

            assert "Invalid scope for token" in exc_info.value.detail
            assert exc_info.value.status_code == 401

        # Test admin role error
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.USER

        with pytest.raises(HTTPException) as exc_info:
            check_admin_role(mock_user)

        assert "Not enough permissions" in exc_info.value.detail
        assert exc_info.value.status_code == 403

    def test_auth_constants_and_dependencies(self):
        """Test auth module constants and dependencies."""
        from src.services.auth import oauth2_scheme, settings
        from src.config import Settings

        # Test OAuth2 scheme exists
        assert oauth2_scheme is not None

        # Test settings is accessible
        assert isinstance(settings, Settings)
        assert hasattr(settings, "secret_key")
        assert hasattr(settings, "algorithm")

    @pytest.mark.asyncio
    async def test_password_reset_token_structure(self):
        """Test password reset token contains required fields."""
        data = {"sub": "test@example.com"}

        with patch("src.services.auth.jwt.encode") as mock_encode:
            with patch("src.services.auth.datetime") as mock_datetime:
                mock_now = datetime(2023, 1, 1, 12, 0, 0)
                mock_datetime.utcnow.return_value = mock_now
                mock_encode.return_value = "token"

                create_password_reset_token(data)

                # Check that encode was called with correct structure
                call_args = mock_encode.call_args[0]
                token_data = call_args[0]

                assert token_data["scope"] == "password_reset"
                assert "sub" in token_data
                assert "exp" in token_data
                assert "iat" in token_data

    def test_user_roles_enum_functionality(self):
        """Test UserRole enum functionality."""
        # Test all enum values
        roles = list(UserRole)
        assert len(roles) == 2  # USER and ADMIN

        # Test string representation
        assert str(UserRole.USER) == "UserRole.USER"
        assert UserRole.USER.name == "USER"
        assert UserRole.USER.value == "user"

        # Test comparison
        assert UserRole.ADMIN != UserRole.USER
        assert UserRole.ADMIN == UserRole.ADMIN
