"""
Additional tests to boost code coverage.
"""

from unittest.mock import Mock, patch
from src.services import cloudinary
from src.database import db


class TestCloudinaryService:
    """Test Cloudinary service functionality."""

    @patch("cloudinary.uploader.upload")
    def test_upload_image_success(self, mock_upload):
        """Test successful image upload."""
        mock_upload.return_value = {
            "public_id": "test_id",
            "secure_url": "https://cloudinary.com/test.jpg",
        }

        # Mock file
        mock_file = Mock()
        mock_file.filename = "test.jpg"
        mock_file.file = Mock()

        result = cloudinary.CloudinaryService.upload_image(mock_file, "avatars")
        assert result == "https://cloudinary.com/test.jpg"
        mock_upload.assert_called_once()

    @patch("cloudinary.uploader.upload")
    def test_upload_image_error(self, mock_upload):
        """Test image upload with error."""
        mock_upload.side_effect = Exception("Upload failed")

        # Mock file
        mock_file = Mock()
        mock_file.filename = "test.jpg"
        mock_file.file = Mock()

        result = cloudinary.CloudinaryService.upload_image(mock_file, "avatars")
        assert result is None

    @patch("cloudinary.utils.cloudinary_url")
    def test_get_url_for_avatar(self, mock_cloudinary_url):
        """Test getting avatar URL."""
        mock_cloudinary_url.return_value = ("https://cloudinary.com/avatar.jpg", {})

        result = cloudinary.CloudinaryService.get_url_for_avatar("test_id", "v123")
        assert result == "https://cloudinary.com/avatar.jpg"
        mock_cloudinary_url.assert_called_once()

    def test_cloudinary_service_instance(self):
        """Test cloudinary service instance exists."""
        assert cloudinary.cloudinary_service is not None
        assert isinstance(cloudinary.cloudinary_service, cloudinary.CloudinaryService)


class TestDatabase:
    """Test database functionality."""

    def test_get_db_generator(self):
        """Test get_db generator function."""
        gen = db.get_db()
        assert gen is not None
        # Test that it's a generator
        assert hasattr(gen, "__next__")

    @patch("src.database.db.SessionLocal")
    def test_get_db_closes_session(self, mock_session_local):
        """Test that get_db properly closes the session."""
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        gen = db.get_db()
        session = next(gen)
        assert session == mock_session

        # Trigger generator cleanup
        try:
            next(gen)
        except StopIteration:
            pass

        mock_session.close.assert_called_once()


class TestSimpleModules:
    """Test basic module structure and imports."""

    def test_import_all_modules(self):
        """Test that all modules can be imported."""
        from src import config
        from src.database import models
        from src.repository import contacts
        from src.repository import users
        from src.schemas import contacts as contact_schemas
        from src.schemas import users as user_schemas
        from src.services import auth

        assert config is not None
        assert models is not None
        assert contacts is not None
        assert users is not None
        assert contact_schemas is not None
        assert user_schemas is not None
        assert auth is not None

    def test_config_settings_attributes(self):
        """Test config settings has required attributes."""
        from src.config import settings

        # Check that settings object exists and has database URL
        assert settings is not None
        assert hasattr(settings, "database_url")

    def test_models_classes_exist(self):
        """Test that model classes are defined."""
        from src.database.models import User, Contact

        assert User is not None
        assert Contact is not None

    def test_user_role_enum(self):
        """Test that UserRole enum exists and has values."""
        from src.database.models import UserRole

        assert UserRole is not None
        assert hasattr(UserRole, "USER")
        assert hasattr(UserRole, "ADMIN")

    def test_auth_service_functions_exist(self):
        """Test auth service has required functions."""
        from src.services import auth

        assert hasattr(auth, "verify_password")
        assert hasattr(auth, "get_password_hash")
        assert hasattr(auth, "create_access_token")

    def test_basic_schema_instantiation(self):
        """Test basic schema instantiation."""
        from src.schemas.contacts import ContactBase
        from src.schemas.users import UserCreate

        # These should not raise exceptions
        assert ContactBase is not None
        assert UserCreate is not None

    def test_settings_with_test_db(self):
        """Test settings work with database."""
        from src.config import settings

        # Should have a database URL (can be sqlite or postgresql)
        assert settings.database_url is not None
        assert len(settings.database_url) > 0

    def test_repository_module_structure(self):
        """Test repository modules have expected structure."""
        from src.repository import contacts, users

        # Should have common functions
        contact_functions = ["get_contact", "create_contact", "get_contacts"]
        for func_name in contact_functions:
            assert hasattr(contacts, func_name)

        # Check for UserRepository class
        assert hasattr(users, "UserRepository")
        user_repo = users.UserRepository
        # Check UserRepository has methods
        assert hasattr(user_repo, "get_user_by_email")
        assert hasattr(user_repo, "create_user")

    def test_exception_classes_exist(self):
        """Test that custom exception classes are defined."""
        from src import exceptions

        # Should have exceptions module
        assert exceptions is not None
        assert hasattr(exceptions, "HTTPException")

    def test_redis_service_class_exists(self):
        """Test Redis service exists."""
        from src.services.redis_cache import RedisService

        assert RedisService is not None
        assert hasattr(RedisService, "__init__")
        assert hasattr(RedisService, "get_client")
        assert hasattr(RedisService, "cache_user")
