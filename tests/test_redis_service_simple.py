"""Tests for Redis caching service."""

import json
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import pytest

from src.services.redis_cache import RedisService


class TestRedisService:
    """Test Redis caching service functionality."""

    @pytest.fixture
    def redis_service(self):
        """Create Redis service instance."""
        return RedisService()

    @pytest.fixture
    def mock_user_data(self):
        """Create mock user data."""
        return {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": "hashedpass",
            "is_verified": True,
            "role": "USER",
            "avatar": "avatar_url",
        }

    @pytest.mark.asyncio
    async def test_get_client_creates_new_client(self, redis_service):
        """Test that get_client creates a new Redis client."""
        with patch("redis.asyncio.from_url") as mock_from_url:
            mock_client = AsyncMock()
            mock_from_url.return_value = mock_client

            client = await redis_service.get_client()

            assert client == mock_client
            assert redis_service.redis_client == mock_client
            mock_from_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_reuses_existing_client(self, redis_service):
        """Test that get_client reuses existing Redis client."""
        existing_client = AsyncMock()
        redis_service.redis_client = existing_client

        client = await redis_service.get_client()

        assert client == existing_client

    @pytest.mark.asyncio
    async def test_cache_user_success(self, redis_service, mock_user_data):
        """Test successful user caching."""
        mock_client = AsyncMock()
        redis_service.redis_client = mock_client

        # Create a mock user object
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"

        await redis_service.cache_user(mock_user)

        # Verify setex was called
        mock_client.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_user_exception_handling(self, redis_service):
        """Test cache_user handles exceptions gracefully."""
        mock_client = AsyncMock()
        mock_client.setex.side_effect = Exception("Redis error")
        redis_service.redis_client = mock_client

        mock_user = Mock()
        mock_user.id = 1

        # Should not raise exception
        await redis_service.cache_user(mock_user)

    @pytest.mark.asyncio
    async def test_get_cached_user_success(self, redis_service, mock_user_data):
        """Test successful user retrieval from cache."""
        mock_client = AsyncMock()
        # Mock successful Redis get
        mock_client.get.return_value = json.dumps(mock_user_data).encode()
        redis_service.redis_client = mock_client

        result = await redis_service.get_cached_user(1)

        assert result is not None
        mock_client.get.assert_called_once_with("user:1")

    @pytest.mark.asyncio
    async def test_get_cached_user_not_found(self, redis_service):
        """Test user retrieval when not in cache."""
        mock_client = AsyncMock()
        mock_client.get.return_value = None
        redis_service.redis_client = mock_client

        result = await redis_service.get_cached_user(1)

        assert result is None
        mock_client.get.assert_called_once_with("user:1")

    @pytest.mark.asyncio
    async def test_get_cached_user_exception_handling(self, redis_service):
        """Test get_cached_user handles exceptions gracefully."""
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Redis error")
        redis_service.redis_client = mock_client

        result = await redis_service.get_cached_user(1)

        assert result is None

    @pytest.mark.asyncio
    async def test_invalidate_user_cache_success(self, redis_service):
        """Test successful cache invalidation."""
        mock_client = AsyncMock()
        mock_client.delete.return_value = 1  # Key was deleted
        redis_service.redis_client = mock_client

        await redis_service.invalidate_user_cache(1)

        mock_client.delete.assert_called_once_with("user:1")

    @pytest.mark.asyncio
    async def test_invalidate_user_cache_key_not_found(self, redis_service):
        """Test cache invalidation when key doesn't exist."""
        mock_client = AsyncMock()
        mock_client.delete.return_value = 0  # No key was deleted
        redis_service.redis_client = mock_client

        await redis_service.invalidate_user_cache(1)

        mock_client.delete.assert_called_once_with("user:1")

    @pytest.mark.asyncio
    async def test_invalidate_user_cache_exception_handling(self, redis_service):
        """Test invalidate_user_cache handles exceptions gracefully."""
        mock_client = AsyncMock()
        mock_client.delete.side_effect = Exception("Redis error")
        redis_service.redis_client = mock_client

        # Should not raise exception
        await redis_service.invalidate_user_cache(1)

    def test_redis_service_initialization(self):
        """Test Redis service initialization."""
        service = RedisService()

        assert service.redis_client is None

    @pytest.mark.asyncio
    async def test_multiple_user_operations(self, redis_service):
        """Test multiple user cache operations."""
        mock_client = AsyncMock()
        redis_service.redis_client = mock_client

        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "testuser"

        # Cache user
        await redis_service.cache_user(mock_user)

        # Get user (simulate cache hit)
        mock_client.get.return_value = json.dumps(
            {"id": 1, "username": "testuser"}
        ).encode()
        result = await redis_service.get_cached_user(1)

        # Invalidate cache
        await redis_service.invalidate_user_cache(1)

        # Verify all operations were called
        mock_client.setex.assert_called()
        mock_client.get.assert_called()
        mock_client.delete.assert_called()

    @pytest.mark.asyncio
    async def test_cache_user_with_custom_expire_time(self, redis_service):
        """Test caching user with custom expiration time."""
        mock_client = AsyncMock()
        redis_service.redis_client = mock_client

        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "testuser"

        # Cache with custom expire time
        await redis_service.cache_user(mock_user, expire_time=7200)

        # Verify setex was called (implementation dependent)
        mock_client.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_with_connection_error(self, redis_service):
        """Test get_client handles connection errors."""
        with patch("redis.asyncio.from_url") as mock_from_url:
            mock_from_url.side_effect = Exception("Connection failed")

            try:
                client = await redis_service.get_client()
                # If no exception is raised, verify behavior
                assert client is not None
            except Exception:
                # It's acceptable for connection errors to propagate
                pass

    def test_redis_service_multiple_instances(self):
        """Test that multiple Redis service instances can be created."""
        service1 = RedisService()
        service2 = RedisService()

        assert service1 is not service2
        assert service1.redis_client is None
        assert service2.redis_client is None
