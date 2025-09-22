import os
import sys
import warnings

# Додаємо батьківську директорію до шляху Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Підавляємо попередження для тестування
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Імпорт основного додатка
try:
    from main import app
    print("✅ Успішно імпортовано FastAPI додаток")
except Exception as e:
    print(f"❌ Помилка імпорту: {e}")
    sys.exit(1)

def test_app_creation():
    """Тест створення додатка"""
    assert app is not None
    print("✅ Додаток створено")

def test_app_title():
    """Тест налаштувань додатка"""
    assert app.title == "Contacts API"
    print("✅ Назва додатка правильна")

def test_app_routes():
    """Тест наявності роутів"""
    routes = [route.path for route in app.routes]
    assert "/" in routes
    assert "/api/contacts/" in routes or any("/api/contacts" in route for route in routes)
    print("✅ Основні роути присутні")

if __name__ == "__main__":
    print("=== Базові тести додатка ===")
    test_app_creation()
    test_app_title()
    test_app_routes()
    print("✅ Всі базові тести пройшли успішно!")
    print("\nДодаток готовий до роботи!")
    print("Для тестування з реальними запитами запустіть сервер:")
    print("poetry run uvicorn main:app --host 127.0.0.1 --port 8001")