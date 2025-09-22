import requests
import time

print("Тестуємо створення дублікату email...")

# Створюємо перший контакт
contact_data = {
    "first_name": "Тест",
    "last_name": "Користувач",
    "email": "test@example.com",
    "phone_number": "+380123456789",
    "birth_date": "1990-01-01",
}

print("1. Створення першого контакту:")
try:
    response = requests.post(
        "http://localhost:8001/api/contacts/", json=contact_data
    )
    print(f"   Статус: {response.status_code}")
    print(f"   Відповідь: {response.json()}")
except Exception as e:
    print(f"   Помилка: {e}")

# Пауза
time.sleep(1)

# Спробуємо створити дублікат
print("\n2. Спроба створення дубліката email:")
duplicate_contact = {
    "first_name": "Інший",
    "last_name": "Користувач", 
    "email": "test@example.com",  # той самий email
    "phone_number": "+380987654321",
    "birth_date": "1985-05-05",
}

try:
    response = requests.post(
        "http://localhost:8001/api/contacts/", json=duplicate_contact
    )
    print(f"   Статус: {response.status_code}")
    print(f"   Відповідь: {response.json()}")
except Exception as e:
    print(f"   Помилка: {e}")

print("\nТест завершено!")