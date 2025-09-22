import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from io import BytesIO
from fastapi import HTTPException, UploadFile, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.routes.auth import (
    signup,
    login,
    confirmed_email,
    request_email,
    read_users_me,
    update_avatar_user,
    request_password_reset,
    reset_password,
)
from src.database.models import User
from src.schemas.users import (
    UserCreate,
    RequestEmail,
    PasswordResetRequest,
    PasswordReset,
)
from src.repository.users import UserRepository


class TestAuthRoutesComprehensive:
    """Comprehensive test auth route handlers directly"""

    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)

    @pytest.fixture
    def mock_user_repo(self):
        repo = Mock(spec=UserRepository)
        # Make all methods async
        repo.get_user_by_email = AsyncMock()
        repo.get_user_by_username = AsyncMock()
        repo.create_user = AsyncMock()
        repo.confirmed_email = AsyncMock()
        repo.update_avatar = AsyncMock()
        repo.update_password = AsyncMock()
        return repo

    @pytest.fixture
    def sample_user(self):
        user = Mock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.hashed_password = "hashed_password"
        user.is_verified = True
        user.avatar = None
        return user

    @pytest.fixture
    def unverified_user(self):
        user = Mock(spec=User)
        user.id = 2
        user.username = "unverified"
        user.email = "unverified@example.com"
        user.hashed_password = "hashed_password"
        user.is_verified = False
        user.avatar = None
        return user

    @pytest.fixture
    def mock_request(self):
        request = Mock(spec=Request)
        request.base_url = "http://localhost:8000/"
        return request

    @pytest.fixture
    def mock_background_tasks(self):
        return Mock(spec=BackgroundTasks)

    @pytest.mark.asyncio
    async def test_signup_success(
        self, mock_user_repo, mock_request, mock_background_tasks, mock_db
    ):
        """Test successful user registration"""
        user_create = UserCreate(
            username="newuser",
            email="new@example.com",
            password="password123",
            first_name="New",
            last_name="User",
        )

        new_user = Mock()
        new_user.email = "new@example.com"
        new_user.username = "newuser"

        mock_user_repo.get_user_by_email.return_value = None
        mock_user_repo.get_user_by_username.return_value = None
        mock_user_repo.create_user.return_value = new_user

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo):
            result = await signup(
                user_create, mock_background_tasks, mock_request, mock_db
            )

        assert result == new_user
        mock_user_repo.get_user_by_email.assert_called_once_with("new@example.com")
        mock_user_repo.get_user_by_username.assert_called_once_with("newuser")
        mock_user_repo.create_user.assert_called_once_with(user_create)
        mock_background_tasks.add_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_signup_email_exists(
        self, mock_user_repo, mock_request, mock_background_tasks, mock_db, sample_user
    ):
        """Test signup with existing email"""
        user_create = UserCreate(
            username="newuser",
            email="test@example.com",
            password="password123",
            first_name="New",
            last_name="User",
        )

        mock_user_repo.get_user_by_email.return_value = sample_user

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo):
            with pytest.raises(HTTPException) as exc_info:
                await signup(user_create, mock_background_tasks, mock_request, mock_db)

        assert exc_info.value.status_code == 409
        assert "Account already exists" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_signup_username_exists(
        self, mock_user_repo, mock_request, mock_background_tasks, mock_db, sample_user
    ):
        """Test signup with existing username"""
        user_create = UserCreate(
            username="testuser",
            email="new@example.com",
            password="password123",
            first_name="New",
            last_name="User",
        )

        mock_user_repo.get_user_by_email.return_value = None
        mock_user_repo.get_user_by_username.return_value = sample_user

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo):
            with pytest.raises(HTTPException) as exc_info:
                await signup(user_create, mock_background_tasks, mock_request, mock_db)

        assert exc_info.value.status_code == 409
        assert "Username already taken" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_success(self, mock_user_repo, mock_db, sample_user):
        """Test successful login"""
        form_data = Mock(spec=OAuth2PasswordRequestForm)
        form_data.username = "testuser"
        form_data.password = "password123"

        mock_user_repo.get_user_by_username.return_value = sample_user

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.verify_password", return_value=True
        ), patch("src.routes.auth.create_access_token", return_value="mock_token"):

            result = await login(form_data, mock_db)

        assert result["access_token"] == "mock_token"
        assert result["token_type"] == "bearer"
        mock_user_repo.get_user_by_username.assert_called_once_with("testuser")

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, mock_user_repo, mock_db):
        """Test login with invalid credentials"""
        form_data = Mock(spec=OAuth2PasswordRequestForm)
        form_data.username = "testuser"
        form_data.password = "wrongpassword"

        mock_user_repo.get_user_by_username.return_value = None

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo):
            with pytest.raises(HTTPException) as exc_info:
                await login(form_data, mock_db)

        assert exc_info.value.status_code == 401
        assert "Incorrect username or password" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_unverified_user(
        self, mock_user_repo, mock_db, unverified_user
    ):
        """Test login with unverified user"""
        form_data = Mock(spec=OAuth2PasswordRequestForm)
        form_data.username = "unverified"
        form_data.password = "password123"

        mock_user_repo.get_user_by_username.return_value = unverified_user

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.verify_password", return_value=True
        ):

            with pytest.raises(HTTPException) as exc_info:
                await login(form_data, mock_db)

        assert exc_info.value.status_code == 401
        assert "Email not verified" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_confirmed_email_success(
        self, mock_user_repo, mock_db, unverified_user
    ):
        """Test successful email confirmation"""
        token = "valid_token"
        email = "test@example.com"

        mock_user_repo.get_user_by_email.return_value = unverified_user
        mock_user_repo.confirmed_email.return_value = None

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.get_email_from_token", return_value=email
        ):

            result = await confirmed_email(token, mock_db)

        assert "Email confirmed" in result["message"]
        mock_user_repo.confirmed_email.assert_called_once_with(email)

    @pytest.mark.asyncio
    async def test_confirmed_email_already_verified(
        self, mock_user_repo, mock_db, sample_user
    ):
        """Test email confirmation for already verified user"""
        token = "valid_token"
        email = "test@example.com"

        mock_user_repo.get_user_by_email.return_value = sample_user

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.get_email_from_token", return_value=email
        ):

            result = await confirmed_email(token, mock_db)

        assert "already confirmed" in result["message"]
        mock_user_repo.confirmed_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_confirmed_email_user_not_found(self, mock_user_repo, mock_db):
        """Test email confirmation with invalid token"""
        token = "invalid_token"
        email = "test@example.com"

        mock_user_repo.get_user_by_email.return_value = None

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.get_email_from_token", return_value=email
        ):

            with pytest.raises(HTTPException) as exc_info:
                await confirmed_email(token, mock_db)

        assert exc_info.value.status_code == 400
        assert "Verification error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_request_email_unverified_user(
        self,
        mock_user_repo,
        mock_db,
        mock_background_tasks,
        mock_request,
        unverified_user,
    ):
        """Test email verification request for unverified user"""
        request_data = RequestEmail(email="test@example.com")

        mock_user_repo.get_user_by_email.return_value = unverified_user

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo):
            result = await request_email(
                request_data, mock_background_tasks, mock_request, mock_db
            )

        assert "Check your email" in result["message"]
        mock_background_tasks.add_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_email_verified_user(
        self, mock_user_repo, mock_db, mock_background_tasks, mock_request, sample_user
    ):
        """Test email verification request for verified user"""
        request_data = RequestEmail(email="test@example.com")

        mock_user_repo.get_user_by_email.return_value = sample_user

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo):
            result = await request_email(
                request_data, mock_background_tasks, mock_request, mock_db
            )

        assert "Check your email" in result["message"]
        mock_background_tasks.add_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_read_users_me(self, sample_user):
        """Test getting current user info"""
        result = await read_users_me(sample_user)
        assert result == sample_user

    @pytest.mark.asyncio
    async def test_update_avatar_success(self, mock_user_repo, mock_db, sample_user):
        """Test successful avatar update"""
        # Create mock file
        file_content = b"fake image content"
        file = Mock(spec=UploadFile)
        file.content_type = "image/jpeg"
        file.file = BytesIO(file_content)

        updated_user = Mock()
        updated_user.avatar = "http://cloudinary.com/avatar.jpg"

        mock_user_repo.update_avatar.return_value = updated_user

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.cloudinary_service.upload_image",
            return_value="http://cloudinary.com/avatar.jpg",
        ):

            result = await update_avatar_user(file, sample_user, mock_db)

        assert result == updated_user
        mock_user_repo.update_avatar.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_avatar_invalid_file_type(self, sample_user, mock_db):
        """Test avatar update with invalid file type"""
        file = Mock(spec=UploadFile)
        file.content_type = "text/plain"

        with pytest.raises(HTTPException) as exc_info:
            await update_avatar_user(file, sample_user, mock_db)

        assert exc_info.value.status_code == 400
        assert "Invalid file type" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_avatar_upload_failed(
        self, mock_user_repo, mock_db, sample_user
    ):
        """Test avatar update when upload fails"""
        file = Mock(spec=UploadFile)
        file.content_type = "image/jpeg"

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.cloudinary_service.upload_image", return_value=None
        ):

            with pytest.raises(HTTPException) as exc_info:
                await update_avatar_user(file, sample_user, mock_db)

        assert exc_info.value.status_code == 400
        assert "Could not upload avatar" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_request_password_reset_existing_user(
        self, mock_user_repo, mock_db, mock_background_tasks, mock_request, sample_user
    ):
        """Test password reset request for existing user"""
        request_data = PasswordResetRequest(email="test@example.com")

        mock_user_repo.get_user_by_email.return_value = sample_user

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.create_password_reset_token", return_value="reset_token"
        ):

            result = await request_password_reset(
                request_data, mock_background_tasks, mock_request, mock_db
            )

        assert "password reset link has been sent" in result["message"]
        mock_background_tasks.add_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_password_reset_nonexistent_user(
        self, mock_user_repo, mock_db, mock_background_tasks, mock_request
    ):
        """Test password reset request for nonexistent user"""
        request_data = PasswordResetRequest(email="nonexistent@example.com")

        mock_user_repo.get_user_by_email.return_value = None

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo):
            result = await request_password_reset(
                request_data, mock_background_tasks, mock_request, mock_db
            )

        assert "password reset link has been sent" in result["message"]
        mock_background_tasks.add_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_reset_password_success(self, mock_user_repo, mock_db, sample_user):
        """Test successful password reset"""
        reset_data = PasswordReset(token="valid_token", new_password="newpassword123")
        email = "test@example.com"

        mock_user_repo.get_user_by_email.return_value = sample_user
        mock_user_repo.update_password.return_value = True

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.verify_password_reset_token", return_value=email
        ):

            result = await reset_password(reset_data, mock_db)

        assert "Password has been reset successfully" in result["message"]
        mock_user_repo.update_password.assert_called_once_with(email, "newpassword123")

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(self, mock_user_repo, mock_db):
        """Test password reset with invalid token"""
        reset_data = PasswordReset(token="invalid_token", new_password="newpassword123")
        email = "test@example.com"

        mock_user_repo.get_user_by_email.return_value = None

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.verify_password_reset_token", return_value=email
        ):

            with pytest.raises(HTTPException) as exc_info:
                await reset_password(reset_data, mock_db)

        assert exc_info.value.status_code == 400
        assert "Invalid reset token" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_reset_password_update_failed(
        self, mock_user_repo, mock_db, sample_user
    ):
        """Test password reset when update fails"""
        reset_data = PasswordReset(token="valid_token", new_password="newpassword123")
        email = "test@example.com"

        mock_user_repo.get_user_by_email.return_value = sample_user
        mock_user_repo.update_password.return_value = False

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.verify_password_reset_token", return_value=email
        ):

            with pytest.raises(HTTPException) as exc_info:
                await reset_password(reset_data, mock_db)

        assert exc_info.value.status_code == 400
        assert "Failed to update password" in str(exc_info.value.detail)


class TestAuthRoutesEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        """Test login with correct user but wrong password"""
        form_data = Mock(spec=OAuth2PasswordRequestForm)
        form_data.username = "testuser"
        form_data.password = "wrongpassword"

        user = Mock()
        user.hashed_password = "correct_hash"
        user.is_verified = True

        mock_user_repo = Mock()
        mock_user_repo.get_user_by_username = AsyncMock(return_value=user)

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.verify_password", return_value=False
        ):

            with pytest.raises(HTTPException) as exc_info:
                await login(form_data, Mock())

        assert exc_info.value.status_code == 401
        assert "Incorrect username or password" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_confirmed_email_token_error(self):
        """Test email confirmation with token processing error"""
        token = "invalid_token"

        with patch(
            "src.routes.auth.get_email_from_token", side_effect=Exception("Token error")
        ):
            with pytest.raises(Exception):
                await confirmed_email(token, Mock())

    @pytest.mark.asyncio
    async def test_avatar_update_png_file(self, sample_user):
        """Test avatar update with PNG file"""
        mock_db = Mock()
        file = Mock(spec=UploadFile)
        file.content_type = "image/png"

        mock_user_repo = Mock()
        mock_user_repo.update_avatar = AsyncMock(return_value=sample_user)

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.cloudinary_service.upload_image",
            return_value="http://example.com/avatar.png",
        ):

            result = await update_avatar_user(file, sample_user, mock_db)

        assert result == sample_user

    @pytest.fixture
    def sample_user(self):
        user = Mock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.hashed_password = "hashed_password"
        user.is_verified = True
        user.avatar = None
        return user

    @pytest.mark.asyncio
    async def test_password_reset_various_scenarios(self):
        """Test password reset token verification scenarios"""
        reset_data = PasswordReset(token="test_token", new_password="newpass")

        # Test when verification raises exception
        with patch(
            "src.routes.auth.verify_password_reset_token",
            side_effect=Exception("Token error"),
        ):
            with pytest.raises(Exception):
                await reset_password(reset_data, Mock())

    @pytest.mark.asyncio
    async def test_request_email_no_user(self):
        """Test email verification request when user doesn't exist"""
        request_data = RequestEmail(email="nonexistent@example.com")
        mock_background_tasks = Mock(spec=BackgroundTasks)
        mock_request = Mock()

        mock_user_repo = Mock()
        mock_user_repo.get_user_by_email = AsyncMock(return_value=None)

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo):
            result = await request_email(
                request_data, mock_background_tasks, mock_request, Mock()
            )

        assert "Check your email" in result["message"]
        mock_background_tasks.add_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_login_password_verification_scenarios(self):
        """Test various password verification scenarios"""
        form_data = Mock(spec=OAuth2PasswordRequestForm)
        form_data.username = "testuser"
        form_data.password = "password123"

        # Test with None user
        mock_user_repo = Mock()
        mock_user_repo.get_user_by_username = AsyncMock(return_value=None)

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo):
            with pytest.raises(HTTPException) as exc_info:
                await login(form_data, Mock())

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_avatar_content_types(self):
        """Test various avatar content types"""
        invalid_types = ["image/gif", "image/bmp", "text/plain", "application/pdf"]

        for content_type in invalid_types:
            file = Mock(spec=UploadFile)
            file.content_type = content_type

            with pytest.raises(HTTPException) as exc_info:
                await update_avatar_user(file, Mock(), Mock())

            assert exc_info.value.status_code == 400
            assert "Invalid file type" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_signup_background_task_call(self):
        """Test that signup properly calls background task"""
        user_create = UserCreate(
            username="newuser",
            email="new@example.com",
            password="password123",
            first_name="New",
            last_name="User",
        )

        new_user = Mock()
        new_user.email = "new@example.com"
        new_user.username = "newuser"

        mock_user_repo = Mock()
        mock_user_repo.get_user_by_email = AsyncMock(return_value=None)
        mock_user_repo.get_user_by_username = AsyncMock(return_value=None)
        mock_user_repo.create_user = AsyncMock(return_value=new_user)

        mock_background_tasks = Mock(spec=BackgroundTasks)
        mock_request = Mock(spec=Request)
        mock_request.base_url = "http://localhost:8000/"

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.send_verification_email_robust"
        ) as mock_send_email:

            result = await signup(
                user_create, mock_background_tasks, mock_request, Mock()
            )

        # Verify background task was added with correct parameters
        mock_background_tasks.add_task.assert_called_once()
        call_args = mock_background_tasks.add_task.call_args
        assert call_args[0][0] == mock_send_email  # First arg should be the function
        assert "new@example.com" in call_args[0]  # Email should be in args
        assert "newuser" in call_args[0]  # Username should be in args


class TestAuthRoutesIntegration:
    """Test integration scenarios"""

    @pytest.mark.asyncio
    async def test_token_creation_in_login(self):
        """Test token creation with proper settings"""
        form_data = Mock(spec=OAuth2PasswordRequestForm)
        form_data.username = "testuser"
        form_data.password = "password123"

        user = Mock()
        user.username = "testuser"
        user.hashed_password = "hashed_password"
        user.is_verified = True

        mock_user_repo = Mock()
        mock_user_repo.get_user_by_username = AsyncMock(return_value=user)

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.verify_password", return_value=True
        ), patch(
            "src.routes.auth.create_access_token", return_value="test_token"
        ) as mock_create_token, patch(
            "src.routes.auth.timedelta"
        ) as mock_timedelta, patch(
            "src.routes.auth.settings"
        ) as mock_settings:

            mock_settings.access_token_expire_minutes = 30
            mock_timedelta.return_value = "mocked_timedelta"

            result = await login(form_data, Mock())

        # Verify token creation was called with correct parameters
        mock_create_token.assert_called_once()
        call_args = mock_create_token.call_args
        assert call_args[1]["data"]["sub"] == "testuser"
        assert call_args[1]["expires_delta"] == "mocked_timedelta"

    @pytest.mark.asyncio
    async def test_password_reset_flow_integration(self):
        """Test complete password reset flow"""
        # Test request password reset
        request_data = PasswordResetRequest(email="test@example.com")
        user = Mock()
        user.email = "test@example.com"
        user.username = "testuser"

        mock_user_repo = Mock()
        mock_user_repo.get_user_by_email = AsyncMock(return_value=user)

        mock_background_tasks = Mock()
        mock_request = Mock()
        mock_request.base_url = "http://localhost:8000/"

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.create_password_reset_token",
            return_value="reset_token_123",
        ) as mock_create_token:

            result = await request_password_reset(
                request_data, mock_background_tasks, mock_request, Mock()
            )

        assert "password reset link has been sent" in result["message"]
        mock_create_token.assert_called_once_with(data={"sub": "test@example.com"})
        mock_background_tasks.add_task.assert_called_once()

        # Test actual password reset
        reset_data = PasswordReset(
            token="reset_token_123", new_password="newpassword123"
        )
        mock_user_repo.update_password = AsyncMock(return_value=True)

        with patch("src.routes.auth.get_user_repo", return_value=mock_user_repo), patch(
            "src.routes.auth.verify_password_reset_token",
            return_value="test@example.com",
        ):

            reset_result = await reset_password(reset_data, Mock())

        assert "Password has been reset successfully" in reset_result["message"]
        mock_user_repo.update_password.assert_called_once_with(
            "test@example.com", "newpassword123"
        )
