"""
Integration tests for auth routes using TestClient.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException, status

from main import app
from src.database.models import User
from src.services.auth import create_access_token


@pytest.fixture
def test_client():
    """Create test client."""
    return TestClient(app)


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


@pytest.fixture
def unconfirmed_user():
    """Unconfirmed test user fixture."""
    return User(
        id=2,
        username="unconfirmed",
        email="unconfirmed@example.com",
        hashed_password="hashed_password",
        is_confirmed=False,
    )


class TestAuthRoutesIntegration:
    """Integration tests for authentication routes."""

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository")
    @patch("src.services.auth.get_password_hash")
    @patch("src.services.email.send_email")
    def test_signup_success(
        self, mock_send_email, mock_hash, mock_repo_class, mock_get_db, test_client
    ):
        """Test successful user signup."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_hash.return_value = "hashed_password"
        mock_send_email.return_value = None

        # Mock repository instance
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_user_by_email.return_value = None  # User doesn't exist

        new_user = User(
            id=1,
            username="newuser",
            email="new@example.com",
            hashed_password="hashed_password",
            is_confirmed=False,
        )
        mock_repo.create_user.return_value = new_user

        # Test data
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
        }

        response = test_client.post("/auth/signup", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert data["is_confirmed"] is False

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository")
    def test_signup_user_exists(
        self, mock_repo_class, mock_get_db, test_client, test_user
    ):
        """Test signup with existing user."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_user_by_email.return_value = test_user  # User exists

        user_data = {
            "username": "existing",
            "email": "test@example.com",
            "password": "password123",
        }

        response = test_client.post("/auth/signup", json=user_data)

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository")
    @patch("src.services.auth.verify_password")
    @patch("src.services.auth.create_access_token")
    @patch("src.services.auth.create_refresh_token")
    def test_login_success(
        self,
        mock_refresh_token,
        mock_access_token,
        mock_verify,
        mock_repo_class,
        mock_get_db,
        test_client,
        test_user,
    ):
        """Test successful login."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_user_by_email.return_value = test_user

        mock_verify.return_value = True
        mock_access_token.return_value = "access_token_123"
        mock_refresh_token.return_value = "refresh_token_123"

        login_data = {"username": "test@example.com", "password": "password123"}

        response = test_client.post("/auth/login", data=login_data)

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "access_token_123"
        assert data["refresh_token"] == "refresh_token_123"
        assert data["token_type"] == "bearer"

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository")
    def test_login_user_not_found(self, mock_repo_class, mock_get_db, test_client):
        """Test login with non-existent user."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_user_by_email.return_value = None  # User not found

        login_data = {"username": "nonexistent@example.com", "password": "password123"}

        response = test_client.post("/auth/login", data=login_data)

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository")
    @patch("src.services.auth.verify_password")
    def test_login_wrong_password(
        self, mock_verify, mock_repo_class, mock_get_db, test_client, test_user
    ):
        """Test login with wrong password."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_user_by_email.return_value = test_user
        mock_verify.return_value = False  # Wrong password

        login_data = {"username": "test@example.com", "password": "wrong_password"}

        response = test_client.post("/auth/login", data=login_data)

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository")
    @patch("src.services.auth.verify_password")
    def test_login_unconfirmed_email(
        self, mock_verify, mock_repo_class, mock_get_db, test_client, unconfirmed_user
    ):
        """Test login with unconfirmed email."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_user_by_email.return_value = unconfirmed_user
        mock_verify.return_value = True

        login_data = {"username": "unconfirmed@example.com", "password": "password123"}

        response = test_client.post("/auth/login", data=login_data)

        assert response.status_code == 401
        assert "Email not confirmed" in response.json()["detail"]

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository")
    @patch("src.services.auth.decode_refresh_token")
    @patch("src.services.auth.create_access_token")
    def test_refresh_token_success(
        self,
        mock_access_token,
        mock_decode,
        mock_repo_class,
        mock_get_db,
        test_client,
        test_user,
    ):
        """Test successful token refresh."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_decode.return_value = "test@example.com"

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_user_by_email.return_value = test_user
        mock_access_token.return_value = "new_access_token_123"

        response = test_client.post(
            "/auth/refresh_token",
            headers={"Authorization": "Bearer refresh_token_here"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "new_access_token_123"
        assert data["token_type"] == "bearer"

    @patch("src.routes.auth.get_db")
    @patch("src.services.auth.decode_refresh_token")
    def test_refresh_token_invalid(self, mock_decode, mock_get_db, test_client):
        """Test refresh with invalid token."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_decode.side_effect = HTTPException(status_code=401, detail="Invalid token")

        response = test_client.post(
            "/auth/refresh_token", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository")
    @patch("src.services.auth.create_email_token")
    @patch("src.services.email.send_email")
    def test_request_email_verification(
        self,
        mock_send_email,
        mock_create_token,
        mock_repo_class,
        mock_get_db,
        test_client,
        unconfirmed_user,
    ):
        """Test email verification request."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_user_by_email.return_value = unconfirmed_user

        mock_create_token.return_value = "email_token_123"
        mock_send_email.return_value = None

        response = test_client.post(
            "/auth/request_email", json={"email": "unconfirmed@example.com"}
        )

        assert response.status_code == 200
        assert "Verification email sent" in response.json()["message"]

    @patch("src.routes.auth.get_db")
    @patch("src.repository.users.UserRepository")
    @patch("src.services.auth.get_email_from_token")
    def test_confirm_email_success(
        self,
        mock_get_email,
        mock_repo_class,
        mock_get_db,
        test_client,
        unconfirmed_user,
    ):
        """Test successful email confirmation."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_email.return_value = "unconfirmed@example.com"

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_user_by_email.return_value = unconfirmed_user
        mock_repo.confirmed_email.return_value = None

        response = test_client.get("/auth/confirmed_email/valid_token")

        assert response.status_code == 200
        assert "Email confirmed" in response.json()["message"]

    @patch("src.routes.auth.get_db")
    @patch("src.services.auth.get_email_from_token")
    def test_confirm_email_invalid_token(
        self, mock_get_email, mock_get_db, test_client
    ):
        """Test email confirmation with invalid token."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_email.side_effect = HTTPException(
            status_code=400, detail="Invalid token"
        )

        response = test_client.get("/auth/confirmed_email/invalid_token")

        assert response.status_code == 400

    @patch("src.routes.auth.get_db")
    @patch("src.routes.auth.get_current_user")
    @patch("src.services.cloudinary.CloudinaryService.upload_image")
    @patch("src.repository.users.UserRepository")
    def test_update_avatar_success(
        self,
        mock_repo_class,
        mock_upload,
        mock_get_user,
        mock_get_db,
        test_client,
        test_user,
    ):
        """Test successful avatar update."""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = test_user
        mock_upload.return_value = "https://cloudinary.com/avatar.jpg"

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        updated_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_confirmed=True,
            avatar_url="https://cloudinary.com/avatar.jpg",
        )
        mock_repo.update_avatar.return_value = updated_user

        # Create mock file
        files = {"file": ("test.jpg", b"fake image data", "image/jpeg")}

        response = test_client.patch(
            "/auth/avatar", files=files, headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["avatar_url"] == "https://cloudinary.com/avatar.jpg"
