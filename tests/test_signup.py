#!/usr/bin/env python3
import requests
import json

# Дані для реєстрації
user_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
}

try:
    # Відправляємо POST запит на реєстрацію
    response = requests.post(
        "http://localhost:8000/auth/signup",
        json=user_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
except Exception as e:
    print(f"Error: {e}")