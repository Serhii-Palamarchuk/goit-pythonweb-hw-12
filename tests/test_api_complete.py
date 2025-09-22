import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("🚀 Testing Contacts API...")
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ GET / - Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ GET / failed: {e}")
        return
    
    # Test 2: Create contact
    print("\n2. Testing contact creation...")
    contact_data = {
        "first_name": "Іван",
        "last_name": "Петренко",
        "email": "ivan@example.com",
        "phone_number": "+380501234567",
        "birth_date": "1990-05-15",
        "additional_data": "Друг з університету"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/contacts/",
            json=contact_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ POST /api/contacts/ - Status: {response.status_code}")
        if response.status_code == 201:
            created_contact = response.json()
            print(f"   Created contact ID: {created_contact.get('id')}")
            contact_id = created_contact.get('id')
        else:
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ POST /api/contacts/ failed: {e}")
        return
    
    # Test 3: Get all contacts
    print("\n3. Testing get all contacts...")
    try:
        response = requests.get(f"{BASE_URL}/api/contacts/")
        print(f"✅ GET /api/contacts/ - Status: {response.status_code}")
        if response.status_code == 200:
            contacts = response.json()
            print(f"   Found {len(contacts)} contacts")
    except Exception as e:
        print(f"❌ GET /api/contacts/ failed: {e}")
    
    # Test 4: Get contact by ID
    if 'contact_id' in locals():
        print(f"\n4. Testing get contact by ID {contact_id}...")
        try:
            response = requests.get(f"{BASE_URL}/api/contacts/{contact_id}")
            print(f"✅ GET /api/contacts/{contact_id} - Status: {response.status_code}")
            if response.status_code == 200:
                contact = response.json()
                print(f"   Contact: {contact['first_name']} {contact['last_name']}")
        except Exception as e:
            print(f"❌ GET /api/contacts/{contact_id} failed: {e}")
    
    # Test 5: Search contacts
    print("\n5. Testing search...")
    try:
        response = requests.get(f"{BASE_URL}/api/contacts/?search=Іван")
        print(f"✅ GET /api/contacts/?search=Іван - Status: {response.status_code}")
        if response.status_code == 200:
            contacts = response.json()
            print(f"   Found {len(contacts)} contacts matching 'Іван'")
    except Exception as e:
        print(f"❌ Search failed: {e}")
    
    # Test 6: Upcoming birthdays
    print("\n6. Testing upcoming birthdays...")
    try:
        response = requests.get(f"{BASE_URL}/api/contacts/birthdays")
        print(f"✅ GET /api/contacts/birthdays - Status: {response.status_code}")
        if response.status_code == 200:
            contacts = response.json()
            print(f"   Found {len(contacts)} contacts with upcoming birthdays")
    except Exception as e:
        print(f"❌ Birthdays test failed: {e}")
    
    print("\n🎉 API testing completed!")

if __name__ == "__main__":
    test_api()