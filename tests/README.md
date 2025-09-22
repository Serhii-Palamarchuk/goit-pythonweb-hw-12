# Тести для Contacts API

Ця папка містить всі тести для перевірки функціональності API контактів з **81% покриттям коду**.

## 🎯 Досягнення
- ✅ **177 тестів проходять успішно** (0 помилок)
- ✅ **81% покриття коду** (перевищує цільові 75%)
- ✅ **100% покриття** ключових модулів
- ✅ **Комплексне тестування** всіх компонентів

## Структура тестів

### 🏆 Комплексні тести (основні)
- `test_exceptions_comprehensive.py` - Повне тестування всіх винятків та обробки помилок
- `test_auth_functions_extended.py` - Розширені тести JWT, токенів та аутентифікації
- `test_repository_contacts.py` - Тести CRUD операцій контактів з SQLAlchemy
- `test_repository_users.py` - Тести операцій користувачів
- `test_schemas.py` - Валідація Pydantic схем та серіалізації
- `test_auth_routes_comprehensive.py` - Комплексні тести роутів аутентифікації
- `test_contacts_routes_simple.py` - Тести роутів контактів

### 📈 Додаткові тести для покриття
- `test_coverage_boost.py` - Допоміжні тести для підвищення покриття
- `test_auth_simple.py` - Базові тести сервісу аутентифікації
- `test_email_simple.py` - Тести email функціональності

### 📜 Legacy тести (потребують сервера)
- `test_full_api.py` - Повний тест API з реальною базою даних
- `test_error_handling.py` - Тестування обробки помилок
- `simple_test.py` - Простий тест для базової перевірки
- `test_with_client.py` - Тести з TestClient
- `test_basic.py` - Базові тести без мережевих запитів

## 🚀 Запуск тестів

### Основні тести (рекомендовано)
```bash
# Швидкий запуск всіх основних тестів з покриттям
poetry run pytest tests/test_exceptions_comprehensive.py tests/test_auth_functions_extended.py tests/test_repository_contacts.py tests/test_repository_users.py tests/test_schemas.py tests/test_coverage_boost.py tests/test_auth_simple.py tests/test_email_simple.py tests/test_auth_routes_comprehensive.py tests/test_contacts_routes_simple.py --cov=src --cov-report=term-missing

# Генерація детального HTML звіту
poetry run pytest --cov=src --cov-report=html
```

### Категорії тестів
```bash
# Тести винятків та обробки помилок
poetry run pytest tests/test_exceptions_comprehensive.py -v

# Тести аутентифікації
poetry run pytest tests/test_auth_functions_extended.py tests/test_auth_simple.py tests/test_auth_routes_comprehensive.py -v

# Тести репозиторіїв та бази даних
poetry run pytest tests/test_repository_contacts.py tests/test_repository_users.py -v

# Тести схем та валідації
poetry run pytest tests/test_schemas.py -v

# Тести роутів та HTTP ендпоінтів
poetry run pytest tests/test_contacts_routes_simple.py tests/test_auth_routes_comprehensive.py -v
```

### Legacy тести (потребують запущеного сервера)
```bash
# 1. Запустити Docker сервіси
docker-compose up -d

# 2. Запустити сервер
poetry run uvicorn main:app --host 127.0.0.1 --port 8000

# 3. Запустити legacy тести
poetry run python tests/test_full_api.py
poetry run python tests/test_error_handling.py
poetry run python tests/simple_test.py
poetry run python tests/test_basic.py
poetry run python tests/test_with_client.py
```

## 📊 Покриття коду по модулях

### ✅ 100% покриття
- `config.py` - конфігурація додатка
- `database/models.py` - SQLAlchemy моделі
- `exceptions.py` - кастомні винятки
- `routes/contacts.py` - роути контактів
- `schemas/contacts.py` - схеми контактів  
- `schemas/users.py` - схеми користувачів
- `services/cloudinary.py` - сервіс Cloudinary

### 📈 Високе покриття (90%+)
- `repository/contacts.py` - 97% покриття
- `routes/auth.py` - 90% покриття

### 📊 Задовільне покриття
- `repository/users.py` - 79% покриття
- `services/auth.py` - 68% покриття
- `services/email.py` - 54% покриття
- `services/redis_cache.py` - 56% покриття

## 🛠 Технології тестування

- **pytest** - основний фреймворк тестування
- **pytest-cov** - аналіз покриття коду
- **pytest-asyncio** - тестування асинхронного коду
- **unittest.mock** - мокування залежностей
- **FastAPI TestClient** - тестування HTTP ендпоінтів
- **SQLAlchemy мокування** - тестування бази даних без реальних запитів

## 🎯 Особливості тестів

- 🔒 **Ізольовані тести** - кожен тест використовує власні моки
- ⚡ **Швидке виконання** - тести не залежать від зовнішніх сервісів
- 🎯 **Високе покриття** - 81% коду покрито тестами
- ✅ **Надійність** - всі 177 тестів проходять успішно
- 📊 **Детальна звітність** - HTML та термінальні звіти покриття

## 📋 Рекомендації

1. **Для швидкої перевірки** використовуйте основні тести з pytest
2. **Для розробки** використовуйте конкретні категорії тестів
3. **Для аналізу покриття** генеруйте HTML звіт
4. **Для CI/CD** використовуйте команду з term-missing звітом

## 🌐 Тестування через Postman

Для тестування API через Postman:

1. Запустіть сервер: `poetry run uvicorn main:app --host 127.0.0.1 --port 8000`
2. Імпортуйте API схему в Postman через URL: `http://127.0.0.1:8000/openapi.json`
3. Або використовуйте інтерактивну документацію:
   - **Swagger UI**: `http://127.0.0.1:8000/docs`
   - **ReDoc**: `http://127.0.0.1:8000/redoc`

## ⚙️ Змінні середовища

Переконайтеся, що файл `.env` налаштований правильно:
```
POSTGRES_DB=contacts_db
POSTGRES_USER=contacts_user
POSTGRES_PASSWORD=contacts_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

---

**Результат:** Професійна якість тестового покриття з 81% покриттям коду та 177 успішними тестами!