"""
Redis caching service for user data.

This module provides caching functionality for user data using Redis,
improving performance by reducing database queries for frequently accessed users.
"""

import json
import pickle
from typing import Optional
import redis.asyncio as redis
from src.config import settings
from src.database.models import User


class RedisService:
    """
    Redis service for caching user data.

    This service provides methods to cache and retrieve user data
    from Redis to improve application performance.
    """

    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client: Optional[redis.Redis] = None

    async def get_client(self) -> redis.Redis:
        """
        Get Redis client instance.

        Returns:
            redis.Redis: Redis client instance
        """
        if not self.redis_client:
            self.redis_client = redis.from_url(
                settings.redis_url, encoding="utf-8", decode_responses=False
            )
        return self.redis_client

    async def cache_user(self, user: User, expire_time: int = 3600) -> None:
        """
        Cache user data in Redis.

        Args:
            user (User): User object to cache
            expire_time (int): Cache expiration time in seconds (default: 1 hour)
        """
        try:
            client = await self.get_client()

            # Convert user to dictionary for JSON serialization
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "hashed_password": user.hashed_password,
                "is_verified": user.is_verified,
                "avatar": user.avatar,
                "role": user.role.value if user.role else "user",
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            }

            # Use email as cache key
            cache_key = f"user:{user.email}"

            # Serialize and cache user data
            serialized_data = pickle.dumps(user_data)
            await client.setex(cache_key, expire_time, serialized_data)

        except Exception as e:
            # Log error but don't break the application
            print(f"Redis cache error: {e}")

    async def get_cached_user(self, email: str) -> Optional[dict]:
        """
        Get cached user data from Redis.

        Args:
            email (str): User email to use as cache key

        Returns:
            Optional[dict]: Cached user data or None if not found
        """
        try:
            client = await self.get_client()
            cache_key = f"user:{email}"

            cached_data = await client.get(cache_key)
            if cached_data:
                return pickle.loads(cached_data)

        except Exception as e:
            # Log error but don't break the application
            print(f"Redis get error: {e}")

        return None

    async def invalidate_user_cache(self, email: str) -> None:
        """
        Remove user data from cache.

        Args:
            email (str): User email to remove from cache
        """
        try:
            client = await self.get_client()
            cache_key = f"user:{email}"
            await client.delete(cache_key)

        except Exception as e:
            # Log error but don't break the application
            print(f"Redis delete error: {e}")

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()


# Global instance
redis_service = RedisService()
