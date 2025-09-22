"""
Unit tests for users repository module.

These tests cover user management operations including
creation, retrieval, email confirmation, and avatar updates.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.models import Base, User, UserRole
from src.repository.users import UserRepository
from src.schemas.users import UserCreate


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def user_repo(db_session):
    """Create a user repository instance."""
    return UserRepository(db_session)


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return UserCreate(
        username="testuser", email="test@example.com", password="testpassword123"
    )


@pytest.mark.asyncio
class TestUserRepository:
    """Test class for user repository functions."""

    async def test_create_user(self, user_repo, test_user_data):
        """Test creating a new user."""
        user = await user_repo.create_user(test_user_data)

        assert user.id is not None
        assert user.username == test_user_data.username
        assert user.email == test_user_data.email
        assert user.hashed_password != test_user_data.password  # Should be hashed
        assert user.is_verified is False
        assert user.role == UserRole.USER
        assert user.avatar is None

    async def test_get_user_by_email(self, user_repo, test_user_data):
        """Test retrieving user by email."""
        # Create user first
        created_user = await user_repo.create_user(test_user_data)

        # Retrieve by email
        retrieved_user = await user_repo.get_user_by_email(test_user_data.email)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == test_user_data.email

    async def test_get_user_by_email_not_found(self, user_repo):
        """Test retrieving user by non-existent email."""
        user = await user_repo.get_user_by_email("nonexistent@example.com")
        assert user is None

    async def test_get_user_by_username(self, user_repo, test_user_data):
        """Test retrieving user by username."""
        # Create user first
        created_user = await user_repo.create_user(test_user_data)

        # Retrieve by username
        retrieved_user = await user_repo.get_user_by_username(test_user_data.username)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == test_user_data.username

    async def test_get_user_by_username_not_found(self, user_repo):
        """Test retrieving user by non-existent username."""
        user = await user_repo.get_user_by_username("nonexistentuser")
        assert user is None

    async def test_confirmed_email(self, user_repo, test_user_data):
        """Test confirming user email."""
        # Create user first
        user = await user_repo.create_user(test_user_data)
        assert user.is_verified is False

        # Confirm email
        await user_repo.confirmed_email(test_user_data.email)

        # Check if email is confirmed
        confirmed_user = await user_repo.get_user_by_email(test_user_data.email)
        assert confirmed_user.is_verified is True

    async def test_confirmed_email_nonexistent_user(self, user_repo):
        """Test confirming email for non-existent user."""
        # Should not raise an exception
        await user_repo.confirmed_email("nonexistent@example.com")

    async def test_update_avatar(self, user_repo, test_user_data):
        """Test updating user avatar."""
        # Create user first
        user = await user_repo.create_user(test_user_data)
        assert user.avatar is None

        # Update avatar
        avatar_url = "https://example.com/avatar.jpg"
        updated_user = await user_repo.update_avatar(test_user_data.email, avatar_url)

        assert updated_user is not None
        assert updated_user.avatar == avatar_url
        assert updated_user.id == user.id

    async def test_update_avatar_nonexistent_user(self, user_repo):
        """Test updating avatar for non-existent user."""
        result = await user_repo.update_avatar(
            "nonexistent@example.com", "https://example.com/avatar.jpg"
        )
        assert result is None

    async def test_user_unique_constraints(self, user_repo, test_user_data):
        """Test that email and username are unique."""
        # Create first user
        await user_repo.create_user(test_user_data)

        # Try to create user with same email
        duplicate_email_user = UserCreate(
            username="differentuser",
            email=test_user_data.email,  # Same email
            password="password123",
        )

        with pytest.raises(Exception):  # Should raise IntegrityError
            await user_repo.create_user(duplicate_email_user)

        # Try to create user with same username
        duplicate_username_user = UserCreate(
            username=test_user_data.username,  # Same username
            email="different@example.com",
            password="password123",
        )

        with pytest.raises(Exception):  # Should raise IntegrityError
            await user_repo.create_user(duplicate_username_user)
