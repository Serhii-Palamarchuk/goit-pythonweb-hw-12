"""
Tests for auth routes.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from src.database.models import User
from src.schemas.users import UserCreate
from src.services.auth import create_access_token


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def test_user():
    """Test user fixture."""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_confirmed=True,
    )


class TestAuthRoutes:
    """Test authentication routes."""

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository.create_user")
    @patch("src.services.auth.get_password_hash")
    def test_signup_success(self, mock_hash, mock_create_user, mock_get_db, client):
        """Test successful user signup."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_hash.return_value = "hashed_password"

        new_user = User(
            id=1,
            username="newuser",
            email="new@example.com",
            hashed_password="hashed_password",
            is_confirmed=False,
        )
        mock_create_user.return_value = new_user

        # Test data
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
        }

        response = client.post("/auth/signup", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository.get_user_by_email")
    def test_signup_user_exists(self, mock_get_user, mock_get_db, client):
        """Test signup with existing user."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        existing_user = User(
            id=1,
            username="existing",
            email="existing@example.com",
            hashed_password="hashed",
            is_confirmed=True,
        )
        mock_get_user.return_value = existing_user

        user_data = {
            "username": "existing",
            "email": "existing@example.com",
            "password": "password123",
        }

        response = client.post("/auth/signup", json=user_data)

        assert response.status_code == 409

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository.get_user_by_email")
    @patch("src.services.auth.verify_password")
    @patch("src.services.auth.create_access_token")
    @patch("src.services.auth.create_refresh_token")
    def test_login_success(
        self,
        mock_refresh_token,
        mock_access_token,
        mock_verify,
        mock_get_user,
        mock_get_db,
        client,
    ):
        """Test successful login."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_confirmed=True,
        )
        mock_get_user.return_value = user
        mock_verify.return_value = True
        mock_access_token.return_value = "access_token"
        mock_refresh_token.return_value = "refresh_token"

        login_data = {"username": "test@example.com", "password": "password123"}

        response = client.post("/auth/login", data=login_data)

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "access_token"
        assert data["refresh_token"] == "refresh_token"
        assert data["token_type"] == "bearer"

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository.get_user_by_email")
    def test_login_user_not_found(self, mock_get_user, mock_get_db, client):
        """Test login with non-existent user."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = None

        login_data = {"username": "nonexistent@example.com", "password": "password123"}

        response = client.post("/auth/login", data=login_data)

        assert response.status_code == 401

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository.get_user_by_email")
    @patch("src.services.auth.verify_password")
    def test_login_wrong_password(
        self, mock_verify, mock_get_user, mock_get_db, client
    ):
        """Test login with wrong password."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_confirmed=True,
        )
        mock_get_user.return_value = user
        mock_verify.return_value = False

        login_data = {"username": "test@example.com", "password": "wrong_password"}

        response = client.post("/auth/login", data=login_data)

        assert response.status_code == 401

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository.get_user_by_email")
    def test_login_unconfirmed_email(self, mock_get_user, mock_get_db, client):
        """Test login with unconfirmed email."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_confirmed=False,
        )
        mock_get_user.return_value = user

        login_data = {"username": "test@example.com", "password": "password123"}

        response = client.post("/auth/login", data=login_data)

        assert response.status_code == 401

    @patch("src.routes.auth.get_db")
    @patch("src.services.auth.decode_refresh_token")
    @patch("src.repository.users.UserRepository.get_user_by_email")
    @patch("src.services.auth.create_access_token")
    def test_refresh_token_success(
        self, mock_access_token, mock_get_user, mock_decode, mock_get_db, client
    ):
        """Test successful token refresh."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_decode.return_value = "test@example.com"

        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_confirmed=True,
        )
        mock_get_user.return_value = user
        mock_access_token.return_value = "new_access_token"

        response = client.post(
            "/auth/refresh_token",
            headers={"Authorization": "Bearer refresh_token_here"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "new_access_token"
        assert data["token_type"] == "bearer"

    @patch("src.routes.auth.get_db")
    @patch("src.services.auth.decode_refresh_token")
    def test_refresh_token_invalid(self, mock_decode, mock_get_db, client):
        """Test refresh with invalid token."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_decode.side_effect = Exception("Invalid token")

        response = client.post(
            "/auth/refresh_token", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository.get_user_by_email")
    @patch("src.services.auth.create_email_token")
    @patch("src.services.email.send_email")
    def test_request_email_success(
        self, mock_send_email, mock_create_token, mock_get_user, mock_get_db, client
    ):
        """Test successful email verification request."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_confirmed=False,
        )
        mock_get_user.return_value = user
        mock_create_token.return_value = "email_token"
        mock_send_email.return_value = None

        response = client.post(
            "/auth/request_email", json={"email": "test@example.com"}
        )

        assert response.status_code == 200

    @patch("src.routes.auth.get_db")
    @patch("src.services.auth.get_email_from_token")
    @patch("src.repository.users.UserRepository.get_user_by_email")
    @patch("src.repository.users.UserRepository.confirmed_email")
    def test_confirm_email_success(
        self, mock_confirm, mock_get_user, mock_get_email, mock_get_db, client
    ):
        """Test successful email confirmation."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_email.return_value = "test@example.com"

        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_confirmed=False,
        )
        mock_get_user.return_value = user
        mock_confirm.return_value = None

        response = client.get("/auth/confirmed_email/test_token")

        assert response.status_code == 200

    @patch("src.routes.auth.get_db")
    @patch("src.services.auth.get_email_from_token")
    def test_confirm_email_invalid_token(self, mock_get_email, mock_get_db, client):
        """Test email confirmation with invalid token."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_email.side_effect = Exception("Invalid token")

        response = client.get("/auth/confirmed_email/invalid_token")

        assert response.status_code == 400
