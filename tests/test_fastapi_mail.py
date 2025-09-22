import asyncio
from pathlib import Path
from pydantic import SecretStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

# Конфігурація з налаштуваннями meta.ua
config = ConnectionConfig(
    MAIL_USERNAME="go-it-test@meta.ua",
    MAIL_PASSWORD=SecretStr("secretPassword1"),
    MAIL_FROM="go-it-test@meta.ua",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.meta.ua",
    MAIL_FROM_NAME="Contacts API",
    MAIL_STARTTLS=False,  # Для SSL використовуємо False
    MAIL_SSL_TLS=True,  # Увімкнути SSL/TLS
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "src" / "services" / "templates",
)


async def test_fastapi_mail():
    print("🧪 Testing FastAPI Mail with meta.ua...")

    try:
        # Тест простого email
        print("1. Testing plain text email...")
        message = MessageSchema(
            subject="Test Email from FastAPI-Mail",
            recipients=["test@example.com"],
            body="This is a test email from FastAPI-Mail with meta.ua SMTP",
            subtype=MessageType.plain,
        )

        fm = FastMail(config)
        await fm.send_message(message)
        print("✅ Plain text email sent successfully!")

        # Тест HTML email
        print("\n2. Testing HTML email...")
        html_content = """
        <html>
            <body>
                <h2>Test HTML Email</h2>
                <p>This is a test HTML email from FastAPI-Mail</p>
                <p><strong>SMTP Server:</strong> smtp.meta.ua</p>
                <p><strong>Port:</strong> 465 (SSL)</p>
            </body>
        </html>
        """

        message_html = MessageSchema(
            subject="Test HTML Email from FastAPI-Mail",
            recipients=["test@example.com"],
            body=html_content,
            subtype=MessageType.html,
        )

        await fm.send_message(message_html)
        print("✅ HTML email sent successfully!")

        # Тест з шаблоном (якщо існує)
        print("\n3. Testing template email...")
        template_folder = Path(__file__).parent / "src" / "services" / "templates"
        if (template_folder / "email_template.html").exists():
            print(f"Template folder found: {template_folder}")

            message_template = MessageSchema(
                subject="Test Template Email",
                recipients=["test@example.com"],
                template_body={
                    "host": "http://localhost:8000",
                    "username": "testuser",
                    "token": "test-token-123",
                },
                subtype=MessageType.html,
            )

            await fm.send_message(message_template, template_name="email_template.html")
            print("✅ Template email sent successfully!")
        else:
            print(f"❌ Template folder not found: {template_folder}")

    except Exception as e:
        print(f"❌ FastAPI Mail failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_fastapi_mail())
