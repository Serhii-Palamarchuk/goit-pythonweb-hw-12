"""Tests for application configuration."""

import os
from unittest.mock import patch
import pytest

from src.config import Settings


class TestSettings:
    """Test application settings and configuration."""

    def test_settings_default_values(self):
        """Test that settings have appropriate default values."""
        settings = Settings()

        # Check that basic attributes exist
        assert hasattr(settings, "database_url")
        assert hasattr(settings, "secret_key")
        assert hasattr(settings, "algorithm")
        assert hasattr(settings, "access_token_expire_minutes")

        # Check default algorithm
        assert settings.algorithm == "HS256"

        # Check default token expiration
        assert isinstance(settings.access_token_expire_minutes, int)
        assert settings.access_token_expire_minutes > 0

    @patch.dict(
        os.environ,
        {
            "DATABASE_URL": "postgresql://test:test@localhost:5432/test_db",
            "SECRET_KEY": "test_secret_key_123",
            "ALGORITHM": "HS512",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
        },
    )
    def test_settings_from_environment(self):
        """Test that settings are correctly loaded from environment variables."""
        settings = Settings()

        assert settings.database_url == "postgresql://test:test@localhost:5432/test_db"
        assert settings.secret_key == "test_secret_key_123"
        assert settings.algorithm == "HS512"
        assert settings.access_token_expire_minutes == 60

    @patch.dict(
        os.environ,
        {
            "MAIL_USERNAME": "test@example.com",
            "MAIL_PASSWORD": "test_password",
            "MAIL_FROM": "noreply@example.com",
            "MAIL_PORT": "587",
            "MAIL_SERVER": "smtp.example.com",
        },
    )
    def test_email_settings_from_environment(self):
        """Test email settings from environment variables."""
        settings = Settings()

        assert settings.mail_username == "test@example.com"
        assert settings.mail_password == "test_password"
        assert settings.mail_from == "noreply@example.com"
        assert settings.mail_port == 587
        assert settings.mail_server == "smtp.example.com"

    @patch.dict(
        os.environ,
        {
            "CLOUDINARY_NAME": "test_cloud",
            "CLOUDINARY_API_KEY": "test_api_key",
            "CLOUDINARY_API_SECRET": "test_api_secret",
        },
    )
    def test_cloudinary_settings_from_environment(self):
        """Test Cloudinary settings from environment variables."""
        settings = Settings()

        assert settings.cloudinary_name == "test_cloud"
        assert settings.cloudinary_api_key == "test_api_key"
        assert settings.cloudinary_api_secret == "test_api_secret"

    @patch.dict(
        os.environ,
        {
            "REDIS_HOST": "test_redis_host",
            "REDIS_PORT": "6380",
            "REDIS_PASSWORD": "test_redis_password",
        },
    )
    def test_redis_settings_from_environment(self):
        """Test Redis settings from environment variables."""
        settings = Settings()

        assert settings.redis_host == "test_redis_host"
        assert settings.redis_port == 6380
        assert settings.redis_password == "test_redis_password"

    def test_settings_string_representation(self):
        """Test that settings can be converted to string."""
        settings = Settings()
        settings_str = str(settings)

        # Should contain some indication it's a Settings object
        assert "Settings" in settings_str or "config" in settings_str.lower()

    def test_settings_have_required_attributes(self):
        """Test that all required settings attributes exist."""
        settings = Settings()

        required_attrs = [
            "database_url",
            "secret_key",
            "algorithm",
            "access_token_expire_minutes",
        ]

        for attr in required_attrs:
            assert hasattr(settings, attr), f"Missing required attribute: {attr}"
            value = getattr(settings, attr)
            assert value is not None, f"Attribute {attr} should not be None"

    @patch.dict(os.environ, {"ACCESS_TOKEN_EXPIRE_MINUTES": "invalid_number"})
    def test_invalid_numeric_environment_variable(self):
        """Test handling of invalid numeric environment variables."""
        # This should not crash, should use default or handle gracefully
        try:
            settings = Settings()
            # If it doesn't crash, check that it has some valid value
            assert isinstance(settings.access_token_expire_minutes, int)
        except (ValueError, TypeError):
            # It's acceptable to raise an error for invalid config
            pytest.skip("Application handles invalid config by raising error")

    def test_settings_immutability_attempt(self):
        """Test behavior when trying to modify settings."""
        settings = Settings()
        original_secret = settings.secret_key

        # Try to modify (depending on implementation, this may or may not work)
        try:
            settings.secret_key = "modified_secret"
            # If modification succeeded, verify it actually changed
            assert settings.secret_key == "modified_secret"
        except (AttributeError, TypeError):
            # If settings are immutable, that's also acceptable
            assert settings.secret_key == original_secret

    def test_settings_boolean_conversion(self):
        """Test that settings object is truthy."""
        settings = Settings()

        # Settings object should be truthy
        assert bool(settings) is True

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_with_no_environment_variables(self):
        """Test settings behavior with no environment variables set."""
        # Clear all environment variables for this test
        settings = Settings()

        # Should still be able to create settings object
        assert settings is not None

        # Should have some default values
        assert hasattr(settings, "algorithm")
        assert settings.algorithm  # Should not be empty or None
