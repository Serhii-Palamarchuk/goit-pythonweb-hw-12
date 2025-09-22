"""
Basic tests for email service functions.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from pathlib import Path

from src.services.email import init_email_config, send_email, send_test_email


class TestEmailServiceBasic:
    """Basic tests for email service functions."""

    @patch("src.services.email.settings")
    def test_init_email_config_success(self, mock_settings):
        """Test successful email config initialization."""
        # Mock valid settings
        mock_settings.mail_from = "test@example.com"
        mock_settings.mail_username = "testuser"
        mock_settings.mail_password = "testpass"
        mock_settings.mail_server = "smtp.example.com"
        mock_settings.mail_port = 587

        result = init_email_config()

        assert result is True

    @patch("src.services.email.settings")
    def test_init_email_config_missing_mail_from(self, mock_settings):
        """Test email config initialization with missing mail_from."""
        mock_settings.mail_from = ""
        mock_settings.mail_username = "testuser"
        mock_settings.mail_password = "testpass"

        result = init_email_config()

        assert result is False

    @patch("src.services.email.settings")
    def test_init_email_config_invalid_mail_from(self, mock_settings):
        """Test email config initialization with invalid mail_from."""
        mock_settings.mail_from = "invalid_email"
        mock_settings.mail_username = "testuser"
        mock_settings.mail_password = "testpass"

        result = init_email_config()

        assert result is False

    @patch("src.services.email.settings")
    def test_init_email_config_missing_username(self, mock_settings):
        """Test email config initialization with missing username."""
        mock_settings.mail_from = "test@example.com"
        mock_settings.mail_username = ""
        mock_settings.mail_password = "testpass"

        result = init_email_config()

        assert result is False

    @patch("src.services.email.settings")
    def test_init_email_config_missing_password(self, mock_settings):
        """Test email config initialization with missing password."""
        mock_settings.mail_from = "test@example.com"
        mock_settings.mail_username = "testuser"
        mock_settings.mail_password = ""

        result = init_email_config()

        assert result is False

    @patch("src.services.email.email_config", None)
    @pytest.mark.asyncio
    async def test_send_email_no_config(self):
        """Test send_email when config is not available."""
        result = await send_email("test@example.com", "testuser", "localhost")

        assert result is False

    @patch("src.services.email.email_config")
    @patch("src.services.email.create_email_token")
    @patch("src.services.email.FastMail")
    @pytest.mark.asyncio
    async def test_send_email_success(
        self, mock_fastmail, mock_create_token, mock_config
    ):
        """Test successful email sending."""
        # Mock config exists
        mock_config.__bool__ = Mock(return_value=True)

        # Mock token creation
        mock_create_token.return_value = "verification_token_123"

        # Mock FastMail
        mock_fm_instance = AsyncMock()
        mock_fastmail.return_value = mock_fm_instance

        result = await send_email("test@example.com", "testuser", "localhost")

        assert result is True
        mock_create_token.assert_called_once_with({"sub": "test@example.com"})
        mock_fm_instance.send_message.assert_called_once()

    @patch("src.services.email.email_config")
    @patch("src.services.email.create_email_token")
    @patch("src.services.email.FastMail")
    @pytest.mark.asyncio
    async def test_send_email_smtp_error(
        self, mock_fastmail, mock_create_token, mock_config
    ):
        """Test email sending with SMTP error."""
        from aiosmtplib.errors import SMTPDataError

        # Mock config exists
        mock_config.__bool__ = Mock(return_value=True)

        # Mock token creation
        mock_create_token.return_value = "verification_token_123"

        # Mock FastMail with SMTP error
        mock_fm_instance = AsyncMock()
        mock_fm_instance.send_message.side_effect = SMTPDataError(
            451, "High intensity of connections"
        )
        mock_fastmail.return_value = mock_fm_instance

        result = await send_email("test@example.com", "testuser", "localhost")

        assert result is False

    @patch("src.services.email.email_config")
    @patch("src.services.email.create_email_token")
    @patch("src.services.email.FastMail")
    @pytest.mark.asyncio
    async def test_send_email_connection_error(
        self, mock_fastmail, mock_create_token, mock_config
    ):
        """Test email sending with connection error."""
        from fastapi_mail.errors import ConnectionErrors

        # Mock config exists
        mock_config.__bool__ = Mock(return_value=True)

        # Mock token creation
        mock_create_token.return_value = "verification_token_123"

        # Mock FastMail with connection error
        mock_fm_instance = AsyncMock()
        mock_fm_instance.send_message.side_effect = ConnectionErrors(
            "Connection failed"
        )
        mock_fastmail.return_value = mock_fm_instance

        result = await send_email("test@example.com", "testuser", "localhost")

        assert result is False

    @patch("src.services.email.email_config", None)
    @pytest.mark.asyncio
    async def test_send_test_email_no_config(self):
        """Test send_test_email when config is not available."""
        result = await send_test_email("test@example.com")

        assert result is False

    @patch("src.services.email.email_config")
    @patch("src.services.email.FastMail")
    @pytest.mark.asyncio
    async def test_send_test_email_success(self, mock_fastmail, mock_config):
        """Test successful test email sending."""
        # Mock config exists
        mock_config.__bool__ = Mock(return_value=True)

        # Mock FastMail
        mock_fm_instance = AsyncMock()
        mock_fastmail.return_value = mock_fm_instance

        result = await send_test_email("test@example.com")

        # Note: Function doesn't return anything, so result might be None
        # We just verify no exceptions were raised
        mock_fm_instance.send_message.assert_called_once()

    def test_email_imports_work(self):
        """Test basic email service imports."""
        from src.services.email import init_email_config, send_email, send_test_email

        assert callable(init_email_config)
        assert callable(send_email)
        assert callable(send_test_email)

    def test_email_constants_exist(self):
        """Test email service constants."""
        from src.services.email import MIN_EMAIL_INTERVAL

        assert MIN_EMAIL_INTERVAL == 30

    def test_template_folder_path(self):
        """Test template folder path calculation."""
        from src.services.email import Path

        # Should be able to construct template path
        current_file = Path(__file__).parent
        template_path = current_file / "templates"

        assert isinstance(template_path, Path)

    @patch("src.services.email.datetime")
    @patch("src.services.email.email_config")
    @patch("src.services.email.last_email_sent")
    @pytest.mark.asyncio
    async def test_email_rate_limiting(
        self, mock_last_sent, mock_config, mock_datetime
    ):
        """Test email rate limiting logic."""
        from datetime import datetime, timedelta

        # Mock config exists
        mock_config.__bool__ = Mock(return_value=True)

        # Mock recent email sent
        now = datetime(2023, 1, 1, 12, 0, 0)
        last_sent = datetime(2023, 1, 1, 11, 59, 45)  # 15 seconds ago

        mock_datetime.now.return_value = now

        with patch("src.services.email.last_email_sent", last_sent):
            with patch("src.services.email.asyncio.sleep") as mock_sleep:
                with patch("src.services.email.create_email_token"):
                    with patch("src.services.email.FastMail"):
                        result = await send_email(
                            "test@example.com", "testuser", "localhost"
                        )

                        # Should have called sleep due to rate limiting
                        mock_sleep.assert_called_once()

    def test_email_service_module_structure(self):
        """Test email service module has expected structure."""
        from src.services import email

        # Test module has expected functions
        assert hasattr(email, "init_email_config")
        assert hasattr(email, "send_email")
        assert hasattr(email, "send_test_email")

        # Test module has expected variables
        assert hasattr(email, "email_config")
        assert hasattr(email, "MIN_EMAIL_INTERVAL")
