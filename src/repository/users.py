"""
User repository module.

This module provides database operations for User entities,
including user creation, authentication, and profile management.
"""

from typing import Optional

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserCreate
from src.services.auth import get_password_hash
from src.services.redis_cache import redis_service


class UserRepository:
    """
    Repository class for user database operations.

    This class encapsulates all database operations related to users,
    providing a clean interface for user management.
    """

    def __init__(self, db: Session):
        """
        Initialize user repository.

        Args:
            db (Session): Database session
        """
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email (str): User's email address

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username (str): User's username

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        return self.db.query(User).filter(User.username == username).first()

    async def create_user(self, user: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user (UserCreate): User data for creation

        Returns:
            User: The newly created user
        """
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def confirmed_email(self, email: str) -> None:
        """
        Mark user email as confirmed.

        Args:
            email (str): User's email address
        """
        user = await self.get_user_by_email(email)
        if user:
            user.is_verified = True
            self.db.commit()
            # Invalidate cache since user data changed
            await redis_service.invalidate_user_cache(email)

    async def update_avatar(self, email: str, url: str) -> Optional[User]:
        """
        Update user avatar.

        Args:
            email (str): User's email address
            url (str): New avatar URL

        Returns:
            Optional[User]: Updated user object or None if not found
        """
        user = await self.get_user_by_email(email)
        if user:
            user.avatar = url
            self.db.commit()
            self.db.refresh(user)
            # Invalidate cache since user data changed
            await redis_service.invalidate_user_cache(email)
        return user

    async def update_password(self, email: str, new_password: str) -> bool:
        """
        Update user password.

        Args:
            email (str): User's email address
            new_password (str): New password (will be hashed)

        Returns:
            bool: True if password updated, False if user not found
        """
        user = await self.get_user_by_email(email)
        if user:
            hashed_password = get_password_hash(new_password)
            user.hashed_password = hashed_password
            self.db.commit()
            # Invalidate cache since user data changed
            await redis_service.invalidate_user_cache(email)
            return True
        return False


def get_user_repo(db: Session) -> UserRepository:
    """
    Get user repository instance.

    Args:
        db (Session): Database session

    Returns:
        UserRepository: User repository instance
    """
    return UserRepository(db)


def get_user_repo(db: Session) -> UserRepository:
    return UserRepository(db)
