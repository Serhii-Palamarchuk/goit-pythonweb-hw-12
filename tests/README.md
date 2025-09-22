# Тести для Contacts API

Ця папка містить всі тести для перевірки функціональності API контактів.

## Структура тестів

### Основні тести
- `test_full_api.py` - Повний тест API з усіма операціями CRUD
- `test_error_handling.py` - Тестування обробки помилок
- `simple_test.py` - Простий тест для перевірки дублікату email
- `test_basic.py` - Базові тести додатка (без мережевих запитів)

### Допоміжні тести
- `test_with_client.py` - Тести з використанням TestClient
- `test_no_db.py` - Тест без бази даних
- `test_api.py` - Базовий тест API
- `test_server.py` - Тест сервера
- `test_api_complete.py` - Повний тест API

## Запуск тестів

### Тестування з реальною базою даних
Перед запуском переконайтеся, що PostgreSQL працює в Docker:
```bash
docker-compose up -d
```

Запустіть сервер:
```bash
poetry run uvicorn main:app --host 127.0.0.1 --port 8000
```

Запустіть тести:
```bash
# Базова перевірка (без сервера і БД)
poetry run python tests/test_basic.py

# Основний тест API
poetry run python tests/test_full_api.py

# Тест обробки помилок
poetry run python tests/test_error_handling.py

# Простий тест
poetry run python tests/simple_test.py
```

### Тестування з TestClient (без реального сервера)
```bash
poetry run python tests/test_with_client.py
```

### Тестування без бази даних
```bash
poetry run python tests/test_no_db.py
```

## Рекомендації

1. **Для швидкої перевірки** використовуйте `test_basic.py` - не потребує сервера або БД
2. **Для розробки** використовуйте `test_with_client.py` - не потребує запуску сервера
3. **Для повного тестування** використовуйте `test_full_api.py` з реальною базою даних
4. **Для тестування помилок** використовуйте `test_error_handling.py`

## Тестування через Postman

Для тестування API через Postman:

1. Запустіть сервер: `poetry run uvicorn main:app --host 127.0.0.1 --port 8000`
2. Імпортуйте API схему в Postman через URL: `http://127.0.0.1:8000/openapi.json`
3. Або використовуйте інтерактивну документацію:
   - **Swagger UI**: `http://127.0.0.1:8000/docs`
   - **ReDoc**: `http://127.0.0.1:8000/redoc`

## Змінні середовища

Переконайтеся, що файл `.env` налаштований правильно:
```
POSTGRES_DB=contacts_db
POSTGRES_USER=contacts_user
POSTGRES_PASSWORD=contacts_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```