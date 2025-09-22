import requests
import time
import json


def test_rate_limiting():
    """Тестуємо rate limiting для маршруту /me"""

    base_url = "http://localhost:8000"

    # 1. Спочатку логінимося
    print("1. Attempting to login...")
    login_data = {"username": "testuser", "password": "testpassword123"}

    try:
        response = requests.post(
            f"{base_url}/api/auth/login", data=login_data, timeout=10
        )
        print(f"Login status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return

        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        print("✅ Login successful")

        # 2. Тестуємо rate limiting
        print("\n2. Testing rate limiting (10 requests per minute)...")

        success_count = 0
        rate_limited_count = 0

        for i in range(1, 16):  # Робимо 15 запитів
            try:
                response = requests.get(
                    f"{base_url}/api/auth/me", headers=headers, timeout=5
                )

                if response.status_code == 200:
                    success_count += 1
                    print(f"Request {i}: ✅ Success (200)")
                elif response.status_code == 429:
                    rate_limited_count += 1
                    print(f"Request {i}: 🚫 Rate limited (429)")
                    try:
                        error_data = response.json()
                        print(f"   Error: {error_data}")
                    except:
                        print(f"   Raw response: {response.text}")
                else:
                    print(f"Request {i}: ❓ Unexpected status ({response.status_code})")
                    print(f"   Response: {response.text}")

            except Exception as e:
                print(f"Request {i}: ❌ Error: {e}")

            time.sleep(0.5)  # Невелика пауза між запитами

        print(f"\n📊 Results:")
        print(f"   Successful requests: {success_count}")
        print(f"   Rate limited requests: {rate_limited_count}")

        if success_count <= 10 and rate_limited_count > 0:
            print("✅ Rate limiting works correctly!")
        elif success_count > 10:
            print("❌ Rate limiting NOT working - too many successful requests")
        else:
            print("❓ Unclear result - check server logs")

    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_rate_limiting()
