import requests
import time


def test_rate_limit_endpoint():
    """Тестуємо rate limiting на тестовому ендпоінті без аутентифікації"""

    base_url = "http://localhost:8001"
    endpoint = f"{base_url}/api/auth/test-rate-limit"

    print("Testing rate limiting on /test-rate-limit endpoint")
    print("Limit: 5 requests per 30 seconds")
    print("=" * 50)

    success_count = 0
    rate_limited_count = 0

    for i in range(1, 8):  # Робимо 7 запитів (більше ніж ліміт 5)
        try:
            response = requests.get(endpoint, timeout=5)

            if response.status_code == 200:
                success_count += 1
                data = response.json()
                print(f"Request {i}: ✅ Success (200) - {data.get('message')}")
            elif response.status_code == 429:
                rate_limited_count += 1
                print(f"Request {i}: 🚫 Rate limited (429)")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Raw response: {response.text}")
            else:
                print(f"Request {i}: ❓ Unexpected ({response.status_code})")
                print(f"   Response: {response.text}")

        except Exception as e:
            print(f"Request {i}: ❌ Error: {e}")

        time.sleep(1)  # Пауза 1 секунда між запитами

    print(f"\n📊 Results:")
    print(f"   Successful requests: {success_count}")
    print(f"   Rate limited requests: {rate_limited_count}")

    if success_count <= 5 and rate_limited_count > 0:
        print("✅ Rate limiting works correctly!")
    elif success_count > 5:
        print("❌ Rate limiting NOT working - too many successful requests")
    else:
        print("❓ Need more requests to test properly")


if __name__ == "__main__":
    test_rate_limit_endpoint()
