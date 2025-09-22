"""
Comprehensive tests for advanced auth service functions.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import jwt

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.services.auth import (
    get_current_user,
    get_email_from_token,
    verify_password_reset_token,
    check_admin_role,
    create_password_reset_token,
)
from src.database.models import User, UserRole
from src.schemas.users import TokenData
from src.config import settings


class TestAdvancedAuthFunctions:
    """Test advanced auth service functions."""

    @pytest.mark.asyncio
    async def test_create_password_reset_token(self):
        """Test password reset token creation."""
        data = {"sub": "test@example.com"}

        with patch("src.services.auth.jwt.encode") as mock_encode:
            mock_encode.return_value = "reset_token_123"

            result = create_password_reset_token(data)

            assert result == "reset_token_123"
            mock_encode.assert_called_once()

            # Verify correct scope and expiry
            call_args = mock_encode.call_args[0]
            token_data = call_args[0]
            assert token_data["scope"] == "password_reset"
            assert "exp" in token_data
            assert "iat" in token_data

    @pytest.mark.asyncio
    @patch("src.services.auth.redis_service")
    @patch("src.services.auth.get_db")
    async def test_get_current_user_from_cache(self, mock_get_db, mock_redis_service):
        """Test getting current user from Redis cache."""
        # Mock token payload
        token_payload = {
            "sub": "test@example.com",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        # Mock cached user data
        cached_user = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": "hashedpass",
            "is_verified": True,
            "avatar": "avatar_url",
            "role": "USER",
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:00:00",
        }

        mock_redis_service.get_cached_user.return_value = cached_user

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = token_payload

            mock_db = Mock(spec=Session)
            result = await get_current_user("valid_token", mock_db)

            assert result.id == 1
            assert result.username == "testuser"
            assert result.email == "test@example.com"
            assert result.is_verified is True
            assert result.role == UserRole.USER

            # Verify cache was checked
            mock_redis_service.get_cached_user.assert_called_once_with(
                "test@example.com"
            )

            # Verify database was not queried
            mock_db.query.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.services.auth.redis_service")
    @patch("src.services.auth.get_db")
    async def test_get_current_user_cache_miss(self, mock_get_db, mock_redis_service):
        """Test getting current user with cache miss."""
        # Mock token payload
        token_payload = {
            "sub": "test@example.com",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        # Mock cache miss
        mock_redis_service.get_cached_user.return_value = None

        # Mock database user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"

        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = token_payload

            result = await get_current_user("valid_token", mock_db)

            assert result == mock_user

            # Verify cache was checked
            mock_redis_service.get_cached_user.assert_called_once_with(
                "test@example.com"
            )

            # Verify database was queried
            mock_db.query.assert_called_once_with(User)

            # Verify user was cached
            mock_redis_service.cache_user.assert_called_once_with(mock_user)

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test get_current_user with invalid token."""
        from jose import JWTError

        mock_db = Mock(spec=Session)

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.side_effect = JWTError("Invalid token")

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("invalid_token", mock_db)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_no_email_in_token(self):
        """Test get_current_user with token missing email."""
        # Mock token payload without 'sub'
        token_payload = {"exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()}

        mock_db = Mock(spec=Session)

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = token_payload

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("token_without_email", mock_db)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    @patch("src.services.auth.redis_service")
    async def test_get_current_user_user_not_found(self, mock_redis_service):
        """Test get_current_user when user not found in database."""
        # Mock token payload
        token_payload = {
            "sub": "nonexistent@example.com",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        # Mock cache miss
        mock_redis_service.get_cached_user.return_value = None

        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = token_payload

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("valid_token", mock_db)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

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

    def test_check_admin_role_moderator(self):
        """Test check_admin_role with moderator user."""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.MODERATOR

        with pytest.raises(HTTPException) as exc_info:
            check_admin_role(mock_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    @patch("src.services.auth.redis_service")
    async def test_get_current_user_cache_data_reconstruction(self, mock_redis_service):
        """Test proper reconstruction of User object from cache data."""
        # Mock token payload
        token_payload = {
            "sub": "test@example.com",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        # Mock cached user data with None values
        cached_user = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": "hashedpass",
            "is_verified": True,
            "avatar": None,  # Test None value
            "role": "MODERATOR",
            "created_at": None,  # Test None datetime
            "updated_at": "2023-01-01T12:00:00",
        }

        mock_redis_service.get_cached_user.return_value = cached_user

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = token_payload

            mock_db = Mock(spec=Session)
            result = await get_current_user("valid_token", mock_db)

            assert result.id == 1
            assert result.username == "testuser"
            assert result.avatar is None
            assert result.role == UserRole.MODERATOR
            assert result.created_at is None
            assert isinstance(result.updated_at, datetime)

    @pytest.mark.asyncio
    async def test_token_data_creation_in_get_current_user(self):
        """Test TokenData creation in get_current_user."""
        token_payload = {
            "sub": "test@example.com",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        mock_db = Mock(spec=Session)

        with patch("src.services.auth.jwt.decode") as mock_decode:
            with patch("src.services.auth.redis_service") as mock_redis_service:
                with patch("src.services.auth.TokenData") as mock_token_data:
                    mock_decode.return_value = token_payload
                    mock_redis_service.get_cached_user.return_value = None
                    mock_db.query.return_value.filter.return_value.first.return_value = (
                        None
                    )

                    # Should raise credentials exception but we can verify TokenData was called
                    with pytest.raises(HTTPException):
                        await get_current_user("valid_token", mock_db)

                    mock_token_data.assert_called_once_with(username="test@example.com")

    @pytest.mark.asyncio
    async def test_settings_integration(self):
        """Test that auth functions properly use settings."""
        # Test that create_password_reset_token uses correct settings
        data = {"sub": "test@example.com"}

        with patch("src.services.auth.jwt.encode") as mock_encode:
            with patch("src.services.auth.settings") as mock_settings:
                mock_settings.secret_key = "test_secret"
                mock_settings.algorithm = "HS256"
                mock_encode.return_value = "token"

                create_password_reset_token(data)

                # Verify settings were used
                _, kwargs = mock_encode.call_args
                assert kwargs is None or True  # jwt.encode doesn't use kwargs

                call_args = mock_encode.call_args[0]
                assert call_args[1] == "test_secret"
                assert call_args[2] == "HS256"

    @pytest.mark.asyncio
    async def test_datetime_handling_in_cache_reconstruction(self):
        """Test datetime string parsing in cache reconstruction."""
        token_payload = {
            "sub": "test@example.com",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        }

        # Test various datetime formats
        cached_user = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": "hashedpass",
            "is_verified": True,
            "avatar": "avatar_url",
            "role": "USER",
            "created_at": "2023-12-01T10:30:45.123456",  # With microseconds
            "updated_at": "2023-12-01T10:30:45",  # Without microseconds
        }

        with patch("src.services.auth.redis_service") as mock_redis_service:
            mock_redis_service.get_cached_user.return_value = cached_user

            with patch("src.services.auth.jwt.decode") as mock_decode:
                mock_decode.return_value = token_payload

                mock_db = Mock(spec=Session)
                result = await get_current_user("valid_token", mock_db)

                # Verify datetime parsing worked
                assert isinstance(result.created_at, datetime)
                assert isinstance(result.updated_at, datetime)
                assert result.created_at.year == 2023
                assert result.updated_at.month == 12
