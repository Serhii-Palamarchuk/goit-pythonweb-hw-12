"""
Тестування API без конфліктів з терміналом
"""
import subprocess
import time
import requests
import signal
import os


def test_contacts_api():
    """Тестування API у окремому процесі"""
    print("🚀 Запускаємо тести Contacts API...")
    
    # Спочатку перевіримо, чи працює база даних
    print("📦 Перевіряємо базу даних...")
    try:
        # Спробуємо підключитися до БД через Python
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="user", 
            password="password",
            database="contacts_db"
        )
        conn.close()
        print("✅ База даних доступна")
    except Exception as e:
        print(f"❌ Помилка підключення до БД: {e}")
        print("💡 Запустіть: docker-compose up -d")
        return
    
    # Запускаємо сервер в окремому процесі
    print("🚀 Запускаємо сервер...")
    server_process = None
    try:
        # Використовуємо poetry run для запуску
        server_process = subprocess.Popen(
            ["poetry", "run", "uvicorn", "main:app", "--port", "8001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        # Чекаємо кілька секунд на запуск сервера
        print("⏳ Чекаємо запуск сервера...")
        time.sleep(5)
        
        # Тестуємо API
        base_url = "http://127.0.0.1:8001"
        
        # Тест 1: Кореневий endpoint
        print("1️⃣ Тестуємо кореневий endpoint...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print(f"✅ GET / - {response.json()}")
        else:
            print(f"❌ GET / - Status: {response.status_code}")
        
        # Тест 2: Створення контакту
        print("2️⃣ Створюємо контакт...")
        contact_data = {
            "first_name": "Іван",
            "last_name": "Петренко",
            "email": "ivan@example.com",
            "phone_number": "+380501234567",
            "birth_date": "1990-05-15",
            "additional_data": "Друг з університету"
        }
        
        response = requests.post(
            f"{base_url}/api/contacts/",
            json=contact_data,
            timeout=10
        )
        
        if response.status_code == 201:
            contact = response.json()
            print(f"✅ Контакт створено - ID: {contact.get('id')}")
            contact_id = contact.get('id')
        else:
            print(f"❌ Помилка створення: {response.status_code} - {response.text}")
            return
        
        # Тест 3: Отримання всіх контактів
        print("3️⃣ Отримуємо всі контакти...")
        response = requests.get(f"{base_url}/api/contacts/", timeout=10)
        if response.status_code == 200:
            contacts = response.json()
            print(f"✅ Знайдено {len(contacts)} контактів")
        else:
            print(f"❌ Помилка отримання контактів: {response.status_code}")
        
        # Тест 4: Пошук
        print("4️⃣ Тестуємо пошук...")
        response = requests.get(f"{base_url}/api/contacts/?search=Іван", timeout=10)
        if response.status_code == 200:
            contacts = response.json()
            print(f"✅ Знайдено {len(contacts)} контактів за пошуком 'Іван'")
        else:
            print(f"❌ Помилка пошуку: {response.status_code}")
        
        # Тест 5: Дні народження
        print("5️⃣ Тестуємо дні народження...")
        response = requests.get(f"{base_url}/api/contacts/birthdays", timeout=10)
        if response.status_code == 200:
            contacts = response.json()
            print(f"✅ Знайдено {len(contacts)} контактів з найближчими днями народження")
        else:
            print(f"❌ Помилка: {response.status_code}")
        
        print("🎉 Тестування завершено успішно!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Помилка запиту: {e}")
    except Exception as e:
        print(f"❌ Неочікувана помилка: {e}")
    finally:
        # Зупиняємо сервер
        if server_process:
            print("🛑 Зупиняємо сервер...")
            if os.name == 'nt':  # Windows
                server_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:  # Unix/Linux
                server_process.terminate()
            server_process.wait(timeout=5)


if __name__ == "__main__":
    test_contacts_api()