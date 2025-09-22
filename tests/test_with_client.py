import sys
from pathlib import Path

# Додаємо батьківську директорію в шлях для імпорту
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Contacts API"}
    print("✅ Root endpoint works!")

def test_create_contact():
    contact_data = {
        "first_name": "Іван",
        "last_name": "Петренко",
        "email": "ivan@example.com",
        "phone_number": "+380501234567",
        "birth_date": "1990-05-15",
        "additional_data": "Друг з університету"
    }
    
    response = client.post("/api/contacts/", json=contact_data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 422:
        print("Validation error details:")
        print(response.json())
    elif response.status_code == 201:
        print("✅ Contact created successfully!")
        print(response.json())
    else:
        print(f"❌ Unexpected status code: {response.status_code}")

if __name__ == "__main__":
    print("Testing API endpoints...")
    test_read_root()
    test_create_contact()