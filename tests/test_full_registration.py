import requests
import json


def test_full_registration_flow():
    """Тестуємо повний процес реєстрації з підтвердженням email"""

    base_url = "http://localhost:8000"

    # 1. Реєстрація користувача
    signup_data = {
        "email": "test.verification@example.com",
        "username": "testverification",
        "password": "testpassword123",
    }

    try:
        print("1. Registering user...")
        response = requests.post(
            f"{base_url}/api/auth/signup", json=signup_data, timeout=10
        )
        print(f"Signup status: {response.status_code}")

        if response.status_code == 201:
            user_data = response.json()
            print(f"✅ User created: {user_data['email']}")
            print(f"   Verified: {user_data['is_verified']}")
            print("   📧 Verification email should be sent!")

        elif response.status_code == 409:
            print("ℹ️  User already exists")

        else:
            print(f"❌ Signup failed: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")


if __name__ == "__main__":
    test_full_registration_flow()
