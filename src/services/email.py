from pathlib import Path
from typing import Optional
import logging
import asyncio
from datetime import datetime, timedelta

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr, SecretStr
from aiosmtplib.errors import SMTPDataError, SMTPRecipientsRefused

from src.config import settings
from src.services.auth import create_email_token

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфігурація email може бути відсутня у разі тестування
email_config: Optional[ConnectionConfig] = None

# Rate limiting для email
last_email_sent = None
MIN_EMAIL_INTERVAL = 30  # секунд між emails


def init_email_config():
    """Initialize email configuration with detailed logging"""
    global email_config

    logger.info("Initializing email config...")
    logger.info(f"MAIL_FROM: {settings.mail_from}")
    logger.info(f"MAIL_SERVER: {settings.mail_server}")
    logger.info(f"MAIL_PORT: {settings.mail_port}")
    logger.info(f"MAIL_USERNAME: {settings.mail_username}")
    password_status = "***" if settings.mail_password else "NOT SET"
    logger.info(f"MAIL_PASSWORD: {password_status}")

    if not settings.mail_from or "@" not in settings.mail_from:
        logger.warning("MAIL_FROM not configured or invalid")
        return False

    if not settings.mail_username:
        logger.warning("MAIL_USERNAME not configured")
        return False

    if not settings.mail_password:
        logger.warning("MAIL_PASSWORD not configured")
        return False

    try:
        email_config = ConnectionConfig(
            MAIL_USERNAME=settings.mail_username,
            MAIL_PASSWORD=SecretStr(settings.mail_password),
            MAIL_FROM=settings.mail_from,
            MAIL_PORT=settings.mail_port,
            MAIL_SERVER=settings.mail_server,
            MAIL_FROM_NAME="Contacts API",
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            TEMPLATE_FOLDER=Path(__file__).parent / "templates",
        )
        logger.info("Email config initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Email configuration error: {e}")
        email_config = None
        return False


# Ініціалізуємо при імпорті
init_email_config()


async def send_email(email: EmailStr, username: str, host: str):
    """Send verification email to user."""
    global last_email_sent

    logger.info(f"Attempting to send email to: {email}")

    if not email_config:
        message = f"Email not configured - cannot send verification to {email}"
        logger.warning(message)
        return False

    # Rate limiting для запобігання блокуванню
    now = datetime.now()
    if last_email_sent and (now - last_email_sent).seconds < MIN_EMAIL_INTERVAL:
        wait_time = MIN_EMAIL_INTERVAL - (now - last_email_sent).seconds
        logger.info(f"Rate limiting: waiting {wait_time} seconds before sending")
        await asyncio.sleep(wait_time)

    try:
        token_verification = create_email_token({"sub": email})
        logger.info(f"Created verification token for {email}")

        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(email_config)
        logger.info(f"Sending email to {email}...")
        await fm.send_message(message, template_name="email_template.html")

        last_email_sent = datetime.now()
        logger.info(f"Email sent successfully to {email}")
        return True

    except SMTPDataError as err:
        if "High intensity of connections" in str(err):
            logger.warning(f"SMTP rate limited: {err}. Email will be retried later")
            # Можна додати retry логіку тут
            return False
        else:
            logger.error(f"SMTP data error: {err}")
            return False
    except ConnectionErrors as err:
        logger.error(f"Email connection failed: {err}")
        return False
    except Exception as err:
        logger.error(f"Email sending failed: {err}")
        return False


async def send_test_email(email: EmailStr):
    """Send test email without template"""
    if not email_config:
        logger.warning("Email not configured for test")
        return False

    try:
        message = MessageSchema(
            subject="Test Email",
            recipients=[email],
            body="This is a test email from Contacts API",
            subtype=MessageType.plain,
        )

        fm = FastMail(email_config)
        await fm.send_message(message)
        logger.info(f"Test email sent successfully to {email}")
        return True

    except Exception as err:
        logger.error(f"Test email failed: {err}")
        return False


async def send_verification_email_robust(email: EmailStr, username: str, host: str):
    """Send verification email with fallback method"""
    logger.info(f"Sending verification email to: {email}")

    # Try template method first
    result = await send_email(email, username, host)
    if result:
        return True

    # If template method fails, try simple method
    logger.info("Template method failed, trying simple method")
    result = await send_simple_verification_email(email, username, host)
    return result


async def send_simple_verification_email(email: EmailStr, username: str, host: str):
    """Send verification email without template (fallback method)"""
    global last_email_sent

    logger.info(f"Sending simple verification email to: {email}")

    if not email_config:
        logger.warning("Email not configured")
        return False

    # Rate limiting
    now = datetime.now()
    if last_email_sent and (now - last_email_sent).seconds < MIN_EMAIL_INTERVAL:
        wait_time = MIN_EMAIL_INTERVAL - (now - last_email_sent).seconds
        logger.info(f"Rate limiting: waiting {wait_time} seconds")
        await asyncio.sleep(wait_time)

    try:
        token_verification = create_email_token({"sub": email})

        # Simple HTML without template
        verify_url = f"{host}api/auth/confirmed_email/{token_verification}"
        html_body = f"""
        <html>
            <body>
                <h2>Welcome to Contacts API, {username}!</h2>
                <p>Please click the link below to verify your email:</p>
                <p><a href="{verify_url}">Verify Email</a></p>
                <p>Or copy this link: {verify_url}</p>
            </body>
        </html>
        """

        message = MessageSchema(
            subject="Confirm your email - Contacts API",
            recipients=[email],
            body=html_body,
            subtype=MessageType.html,
        )

        fm = FastMail(email_config)
        await fm.send_message(message)

        last_email_sent = datetime.now()
        logger.info(f"Simple verification email sent to {email}")
        return True

    except SMTPDataError as err:
        if "High intensity of connections" in str(err):
            logger.warning(f"SMTP rate limited: {err}")
            return False
        else:
            logger.error(f"SMTP data error: {err}")
            return False
    except Exception as err:
        logger.error(f"Simple email failed: {err}")
        return False
