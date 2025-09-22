import requests


def test_unverified_user_login():
    """Тестуємо що неверифіковані користувачі не можуть залогінитися"""

    base_url = "http://localhost:8000"

    # 1. Створюємо нового користувача (буде неверифікований)
    signup_data = {
        "email": "unverified.test@example.com",
        "username": "unverifieduser",
        "password": "testpassword123",
    }

    print("1. Creating unverified user...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/signup", json=signup_data, timeout=10
        )
        print(f"Signup status: {response.status_code}")

        if response.status_code == 201:
            user_data = response.json()
            print(f"✅ User created: {user_data['email']}")
            print(f"   Verified: {user_data['is_verified']}")

            # 2. Спробуємо залогінитися з неверифікованим акаунтом
            print("\n2. Attempting login with unverified account...")
            login_data = {
                "username": signup_data["username"],
                "password": signup_data["password"],
            }

            # FastAPI OAuth2PasswordRequestForm очікує form data, не JSON
            response = requests.post(
                f"{base_url}/api/auth/login",
                data=login_data,  # використовуємо data замість json
                timeout=10,
            )

            print(f"Login status: {response.status_code}")
            print(f"Response: {response.text}")

            if response.status_code == 401:
                print("✅ SUCCESS: Unverified user cannot login!")
            else:
                print("❌ FAILED: Unverified user was able to login")

        elif response.status_code == 409:
            print("ℹ️  User already exists, testing login...")

            # Якщо користувач вже існує, просто тестуємо логін
            login_data = {
                "username": signup_data["username"],
                "password": signup_data["password"],
            }

            response = requests.post(
                f"{base_url}/api/auth/login", data=login_data, timeout=10
            )

            print(f"Login status: {response.status_code}")
            print(f"Response: {response.text}")

            if response.status_code == 401:
                print("✅ SUCCESS: Unverified user cannot login!")
            else:
                print("❌ FAILED: Unverified user was able to login")

        else:
            print(f"❌ Signup failed: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")


if __name__ == "__main__":
    test_unverified_user_login()
