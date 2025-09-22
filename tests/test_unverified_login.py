import requests
import json

def test_unverified_login():
    """Тестуємо що неверифіковані користувачі не можуть залогінитися"""
    
    base_url = "http://localhost:8001"
    
    # 1. Створюємо нового користувача (буде неверифікований)
    signup_data = {
        "email": "unverified.test@example.com",
        "username": "unverifieduser", 
        "password": "testpassword123"
    }
    
    print("1. Creating unverified user...")
    try:
        response = requests.post(f"{base_url}/api/auth/signup", json=signup_data, timeout=10)
        print(f"Signup status: {response.status_code}")
        
        if response.status_code == 201:
            user_data = response.json()
            print(f"✅ User created: {user_data['email']}")
            print(f"   Verified: {user_data['is_verified']}")
            
            # 2. Спробуємо залогінитися з неверифікованим акаунтом
            print("\n2. Attempting login with unverified account...")
            login_data = {
                "username": signup_data["username"],
                "password": signup_data["password"]
            }
            
            response = requests.post(
                f"{base_url}/api/auth/login", 
                data=login_data,  # OAuth2PasswordRequestForm expects form data
                timeout=10
            )
            
            print(f"Login status: {response.status_code}")
            if response.status_code == 401:
                error_data = response.json()
                print(f"✅ Login blocked: {error_data['detail']}")
            else:
                print(f"❌ Login should be blocked but got: {response.text}")
                
        elif response.status_code == 409:
            print("ℹ️  User already exists, testing login...")
            
            # Спробуємо залогінитися з існуючим користувачем
            login_data = {
                "username": signup_data["username"],
                "password": signup_data["password"]
            }
            
            response = requests.post(
                f"{base_url}/api/auth/login", 
                data=login_data,
                timeout=10
            )
            
            print(f"Login status: {response.status_code}")
            if response.status_code == 401:
                error_data = response.json()
                print(f"✅ Login blocked: {error_data['detail']}")
            else:
                print(f"Result: {response.text}")
        else:
            print(f"❌ Signup failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_unverified_login()