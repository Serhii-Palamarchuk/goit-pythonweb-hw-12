import requests

# Тестування реєстрації користувача
url = "http://localhost:8000/auth/signup"
data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123",
}

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except requests.RequestException as e:
    print(f"Request Error: {e}")
except Exception as e:
    print(f"Unexpected Error: {e}")
