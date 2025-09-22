import asyncio
import logging
from src.services.email import send_verification_email_robust

# Налаштування логування
logging.basicConfig(level=logging.INFO)


async def test_robust_email():
    print("🧪 Testing robust email verification...")

    result = await send_verification_email_robust(
        email="test@example.com", username="testuser", host="http://localhost:8000"
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(test_robust_email())
