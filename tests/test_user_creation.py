import requests


def create_and_test_user():
    """Створюємо користувача і тестуємо rate limiting"""

    base_url = "http://localhost:8000"

    # 1. Створюємо користувача
    print("1. Creating user...")
    signup_data = {
        "email": "ratelimit.test@example.com",
        "username": "ratelimituser",
        "password": "testpassword123",
    }

    try:
        response = requests.post(
            f"{base_url}/api/auth/signup", json=signup_data, timeout=10
        )
        print(f"Signup status: {response.status_code}")

        if response.status_code == 201:
            print("✅ User created successfully")
        elif response.status_code == 409:
            print("ℹ️  User already exists")
        else:
            print(f"❌ Signup failed: {response.text}")

        # 2. Підтверджуємо email вручну (для тесту)
        print("\n2. Note: Email verification is required for login")
        print("   For testing, you can manually verify the user in database")
        print("   Or use an existing verified user")

        # 3. Спробуємо логін з неверифікованим користувачем
        print("\n3. Attempting login with unverified user...")
        login_data = {
            "username": signup_data["username"],
            "password": signup_data["password"],
        }

        response = requests.post(
            f"{base_url}/api/auth/login", data=login_data, timeout=10
        )
        print(f"Login status: {response.status_code}")

        if response.status_code == 401:
            response_data = response.json()
            if "Email not verified" in response_data.get("detail", ""):
                print("ℹ️  Expected: Email not verified")
                print("   To test rate limiting, we need a verified user")
            else:
                print(f"❌ Login failed: {response.text}")
        elif response.status_code == 200:
            print("✅ Login successful - can test rate limiting")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    create_and_test_user()
