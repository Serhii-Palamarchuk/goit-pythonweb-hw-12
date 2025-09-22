"""
Integration test for refresh token endpoint.

This test verifies that the /auth/refresh endpoint works correctly
with real HTTP requests.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app
from src.database.models import User, UserRole
from src.services.auth import create_refresh_token


def test_refresh_endpoint_success():
    """Test successful token refresh via API endpoint."""

    client = TestClient(app)

    # Create a valid refresh token
    refresh_token = create_refresh_token({"sub": "test@example.com"})

    # Mock the user repository
    mock_user = User()
    mock_user.id = 1
    mock_user.username = "testuser"
    mock_user.email = "test@example.com"
    mock_user.is_verified = True
    mock_user.role = UserRole.USER

    with patch(
        "src.repository.users.UserRepository.get_user_by_email", new_callable=AsyncMock
    ) as mock_get_user:
        mock_get_user.return_value = mock_user

        # Make request to refresh endpoint
        response = client.post(
            "/api/auth/refresh", json={"refresh_token": refresh_token}
        )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

    # Verify tokens are not empty
    assert len(data["access_token"]) > 50
    assert len(data["refresh_token"]) > 50

    # Verify tokens are different
    assert data["access_token"] != data["refresh_token"]
    assert data["refresh_token"] != refresh_token  # New refresh token


def test_refresh_endpoint_invalid_token():
    """Test refresh endpoint with invalid token."""

    client = TestClient(app)

    response = client.post(
        "/api/auth/refresh", json={"refresh_token": "invalid.token.here"}
    )

    assert response.status_code == 422
    data = response.json()
    assert "Invalid token" in data["detail"]


def test_refresh_endpoint_access_token_as_refresh():
    """Test that access token cannot be used for refresh."""

    client = TestClient(app)

    from src.services.auth import create_access_token

    # Create access token instead of refresh token
    access_token = create_access_token({"sub": "test@example.com"})

    response = client.post("/api/auth/refresh", json={"refresh_token": access_token})

    assert response.status_code == 401
    data = response.json()
    assert "Invalid scope for token" in data["detail"]


def test_refresh_endpoint_user_not_found():
    """Test refresh endpoint when user is not found."""

    client = TestClient(app)

    refresh_token = create_refresh_token({"sub": "nonexistent@example.com"})

    with patch(
        "src.repository.users.UserRepository.get_user_by_email", new_callable=AsyncMock
    ) as mock_get_user:
        mock_get_user.return_value = None

        response = client.post(
            "/api/auth/refresh", json={"refresh_token": refresh_token}
        )

    assert response.status_code == 401
    data = response.json()
    assert "User not found" in data["detail"]


if __name__ == "__main__":
    pytest.main([__file__])
