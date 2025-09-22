import requests
import json

# Test data
contact_data = {
    "first_name": "Іван",
    "last_name": "Петренко", 
    "email": "ivan@example.com",
    "phone_number": "+380501234567",
    "birth_date": "1990-05-15",
    "additional_data": "Друг з університету"
}

try:
    # Test root endpoint
    response = requests.get("http://127.0.0.1:8002/")
    print("GET / Response:", response.status_code, response.json())
    
    # Test POST endpoint
    response = requests.post(
        "http://127.0.0.1:8002/api/contacts/",
        json=contact_data,
        headers={"Content-Type": "application/json"}
    )
    
    print("POST /api/contacts/ Response:", response.status_code)
    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Error:", response.text)
        
except requests.exceptions.ConnectionError:
    print("Cannot connect to server. Make sure it's running on port 8002")
except Exception as e:
    print("Error:", e)