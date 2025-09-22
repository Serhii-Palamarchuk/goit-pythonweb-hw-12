# Contacts API

REST API для управління контактами з аутентифікацією та авторизацією, побудований з використанням FastAPI та SQLAlchemy.

## Функціональність

### Основні функції:
- **Аутентифікація та авторизація** з використанням JWT токенів
- **Реєстрація користувачів** з верифікацією email
- **CRUD операції для контактів** (доступ тільки до власних контактів)
- **Пошук контактів** за ім'ям, прізвищем або email
- **Дні народження** - отримання контактів з днями народження на найближчі 7 днів
- **Завантаження аватарів** через Cloudinary
- **Rate limiting** для обмеження кількості запитів
- **CORS** підтримка для роботи з фронтендом
- **Email верифікація** для підтвердження реєстрації

### Технічні особливості:
- Хешування паролів за допомогою bcrypt
- JWT токени для авторизації
- PostgreSQL база даних
- Redis для rate limiting
- Cloudinary для зберігання зображень
- Docker Compose для легкого розгортання
- Автоматична генерація Swagger документації

## Структура проекту

```
src/
├── database/           # Конфігурація бази даних та моделі
│   ├── db.py          # Налаштування підключення до БД
│   └── models.py      # SQLAlchemy моделі (User, Contact)
├── repository/        # Репозиторій для роботи з даними
│   ├── contacts.py    # CRUD операції для контактів
│   └── users.py       # CRUD операції для користувачів
├── routes/           # API роутери
│   ├── contacts.py   # Ендпоінти для контактів
│   └── auth.py       # Ендпоінти для аутентифікації
├── schemas/          # Pydantic схеми для валідації
│   ├── contacts.py   # Схеми для контактів
│   └── users.py      # Схеми для користувачів
├── services/         # Бізнес-логіка та сервіси
│   ├── auth.py       # JWT аутентифікація
│   ├── email.py      # Відправка email
│   └── cloudinary.py # Робота з Cloudinary
├── exceptions.py     # Обробка помилок
└── config.py         # Конфігурація додатка
tests/                # Тести (81% покриття коду)
├── test_full_api.py  # Повний тест API
├── test_error_handling.py # Тест обробки помилок
├── simple_test.py    # Простий тест
├── test_exceptions_comprehensive.py # Комплексні тести винятків
├── test_auth_functions_extended.py # Розширені тести аутентифікації
├── test_repository_contacts.py # Тести репозиторію контактів
├── test_repository_users.py # Тести репозиторію користувачів
├── test_schemas.py   # Тести Pydantic схем
├── test_coverage_boost.py # Додаткові тести для покриття
├── test_auth_simple.py # Базові тести аутентифікації
├── test_email_simple.py # Тести email сервісу
├── test_auth_routes_comprehensive.py # Комплексні тести роутів аутентифікації
├── test_contacts_routes_simple.py # Тести роутів контактів
└── README.md         # Документація тестів
main.py               # Головний файл додатка
pyproject.toml        # Poetry конфігурація та залежності
docker-compose.yml    # Docker Compose конфігурація
Dockerfile            # Docker конфігурація
.env.example          # Приклад налаштувань середовища
```

## Тестування та якість коду

### Покриття тестами
Проект має **81% покриття коду** з комплексними тестами:

#### Статистика покриття по модулях:
- ✅ **100% покриття:**
  - `config.py` - конфігурація додатка
  - `database/models.py` - SQLAlchemy моделі
  - `exceptions.py` - кастомні винятки
  - `routes/contacts.py` - роути контактів
  - `schemas/contacts.py` - схеми контактів
  - `schemas/users.py` - схеми користувачів
  - `services/cloudinary.py` - сервіс Cloudinary

- 📈 **Високе покриття (90%+):**
  - `repository/contacts.py` - 97% покриття
  - `routes/auth.py` - 90% покриття

- 📊 **Задовільне покриття:**
  - `repository/users.py` - 79% покриття
  - `services/auth.py` - 68% покриття
  - `services/email.py` - 54% покриття
  - `services/redis_cache.py` - 56% покриття

### Структура тестів

#### Комплексні тести (основні)
- `test_exceptions_comprehensive.py` - Повне тестування всіх винятків
- `test_auth_functions_extended.py` - Розширені тести JWT та аутентифікації
- `test_repository_contacts.py` - Тести CRUD операцій контактів
- `test_repository_users.py` - Тести операцій користувачів
- `test_schemas.py` - Валідація Pydantic схем
- `test_auth_routes_comprehensive.py` - Комплексні тести роутів аутентифікації
- `test_contacts_routes_simple.py` - Тести роутів контактів

#### Додаткові тести
- `test_coverage_boost.py` - Допоміжні тести для підвищення покриття
- `test_auth_simple.py` - Базові тести сервісу аутентифікації
- `test_email_simple.py` - Тести email функціональності

#### Legacy тести
- `test_full_api.py` - Повний тест API з реальною базою даних
- `test_error_handling.py` - Тестування обробки помилок
- `simple_test.py` - Простий тест для базової перевірки

### Запуск тестів

#### Всі тести з покриттям
```bash
# Запуск всіх основних тестів з покриттям
poetry run pytest tests/test_exceptions_comprehensive.py tests/test_auth_functions_extended.py tests/test_repository_contacts.py tests/test_repository_users.py tests/test_schemas.py tests/test_coverage_boost.py tests/test_auth_simple.py tests/test_email_simple.py tests/test_auth_routes_comprehensive.py tests/test_contacts_routes_simple.py --cov=src --cov-report=term-missing

# Генерація HTML звіту з покриттям
poetry run pytest --cov=src --cov-report=html
# Результат: htmlcov/index.html
```

#### Окремі категорії тестів
```bash
# Тести винятків та обробки помилок
poetry run pytest tests/test_exceptions_comprehensive.py -v

# Тести аутентифікації
poetry run pytest tests/test_auth_functions_extended.py tests/test_auth_simple.py tests/test_auth_routes_comprehensive.py -v

# Тести репозиторіїв
poetry run pytest tests/test_repository_contacts.py tests/test_repository_users.py -v

# Тести схем та валідації
poetry run pytest tests/test_schemas.py -v

# Тести роутів
poetry run pytest tests/test_contacts_routes_simple.py tests/test_auth_routes_comprehensive.py -v
```

#### Legacy тести (потребують запущеного сервера)
```bash
# Запустити Docker сервіси
docker-compose up -d

# Запустити сервер
poetry run uvicorn main:app --host 127.0.0.1 --port 8000

# Повний API тест
poetry run python tests/test_full_api.py

# Тест обробки помилок
poetry run python tests/test_error_handling.py

# Простий тест
poetry run python tests/simple_test.py
```

### Технології тестування
- **pytest** - основний фреймворк тестування
- **pytest-cov** - аналіз покриття коду
- **pytest-asyncio** - тестування асинхронного коду
- **unittest.mock** - мокування залежностей
- **FastAPI TestClient** - тестування HTTP ендпоінтів
- **SQLAlchemy мокування** - тестування бази даних без реальних запитів

### Особливості тестів
- 🔒 **Ізольовані тести** - кожен тест використовує власні моки
- ⚡ **Швидке виконання** - тести не залежать від зовнішніх сервісів
- 🎯 **Високе покриття** - 81% коду покрито тестами
- ✅ **Надійність** - всі 177 тестів проходять успішно
- 📊 **Детальна звітність** - HTML та термінальні звіти покриття

## API Ендпоінти

### Аутентифікація
- `POST /api/auth/signup` - Реєстрація нового користувача
- `POST /api/auth/login` - Логін користувача (отримання JWT токена)
- `GET /api/auth/confirmed_email/{token}` - Підтвердження email
- `POST /api/auth/request_email` - Повторне відправлення email для підтвердження
- `POST /api/auth/request-password-reset` - Запит на скидання пароля
- `POST /api/auth/reset-password` - Скидання пароля за токеном
- `GET /api/auth/me` - Отримання інформації про поточного користувача (rate limited: 10/min)
- `PATCH /api/auth/avatar` - Оновлення аватара користувача

### Контакти (потребують аутентифікації)
- `GET /api/contacts/` - Отримання списку контактів користувача
- `POST /api/contacts/` - Створення нового контакту
- `GET /api/contacts/{contact_id}` - Отримання контакту за ID
- `PUT /api/contacts/{contact_id}` - Оновлення контакту
- `DELETE /api/contacts/{contact_id}` - Видалення контакту
- `GET /api/contacts/birthdays` - Контакти з днями народження на найближчі 7 днів

### Пошук
- `GET /api/contacts/?search=query` - Пошук контактів за ім'ям, прізвищем або email

## Налаштування та запуск

### 1. Клонування репозиторію
```bash
git clone <repository-url>
cd goit-pythonweb-hw-10
```

### 2. Налаштування змінних середовища
```bash
# Скопіюйте файл прикладу
cp .env.example .env

# Відредагуйте .env файл з вашими налаштуваннями
```

### 3. Запуск з Docker Compose (Рекомендовано)

#### Швидкий старт з готовим образом:
```bash
# Запустити всі сервіси з готовим образом з Docker Hub
docker-compose up -d

# Переглянути логи
docker-compose logs -f api

# Зупинити сервіси
docker-compose down
```

#### Розробка з локальною збіркою:
```bash
# Використати локальну збірку для розробки
docker-compose -f docker-compose.dev.yml up -d

# Або змінити docker-compose.yml на використання build: .
```

#### Публікація власного образу:
```bash
# Linux/Mac
chmod +x build-and-push.sh
./build-and-push.sh [версія]

# Windows
build-and-push.bat [версія]

# Приклади:
./build-and-push.sh v1.0.0
./build-and-push.sh latest
```

### 4. Локальний запуск (альтернативний спосіб)
```bash
# Встановити залежності
poetry install

# Запустити PostgreSQL та Redis (через Docker або локально)
docker run -d --name contacts_db -p 5432:5432 -e POSTGRES_DB=contacts_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password postgres:15-alpine
docker run -d --name contacts_redis -p 6379:6379 redis:7-alpine

# Запустити додаток
poetry run uvicorn main:app --reload
```

### 5. Доступ до API
- **API**: http://localhost:8000
- **Swagger документація**: http://localhost:8000/docs
- **ReDoc документація**: http://localhost:8000/redoc

### 6. Налаштування зовнішніх сервісів

#### Email (Gmail)
1. Увімкніть 2-Factor Authentication
2. Створіть App Password
3. Додайте налаштування до .env:
```
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
```

#### Cloudinary
1. Створіть аккаунт на [Cloudinary](https://cloudinary.com)
2. Отримайте API ключі з Dashboard
3. Додайте до .env:
```
CLOUDINARY_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

## Docker

### Готовий образ
Додаток доступний в Docker Hub:
```bash
docker pull serhiipalamarchuk/goit-pythonweb-hw-10:latest
```

### Файли Docker
- `Dockerfile` - для розробки з live reload
- `Dockerfile.prod` - для production без dev залежностей
- `docker-compose.yml` - використовує готовий образ з Docker Hub
- `docker-compose.dev.yml` - для локальної розробки з збіркою

### Збірка та публікація
```bash
# Швидка збірка та публікація
./build-and-push.sh v1.0.0

# Ручна збірка
docker build -t serhiipalamarchuk/goit-pythonweb-hw-10:latest -f Dockerfile.prod .

# Публікація
docker push serhiipalamarchuk/goit-pythonweb-hw-10:latest
```

## Poetry команди

### Основні команди
```bash
# Встановити всі залежності
poetry install

# Додати нову залежність
poetry add package_name

# Додати залежність для розробки
poetry add --group dev package_name

# Активувати віртуальне середовище
poetry shell

# Запустити команду у віртуальному середовищі
poetry run command

# Показати інформацію про проект
poetry show

# Оновити залежності
poetry update
```

### Скрипти проекту
```bash
# Запустити сервер
poetry run uvicorn main:app --reload

# Форматування коду
poetry run black src/

# Сортування імпортів
poetry run isort src/

# Лінтинг
poetry run flake8 src/

# === ТЕСТУВАННЯ ===

# Швидкий запуск всіх основних тестів з покриттям (рекомендовано)
poetry run pytest tests/test_exceptions_comprehensive.py tests/test_auth_functions_extended.py tests/test_repository_contacts.py tests/test_repository_users.py tests/test_schemas.py tests/test_coverage_boost.py tests/test_auth_simple.py tests/test_email_simple.py tests/test_auth_routes_comprehensive.py tests/test_contacts_routes_simple.py --cov=src --cov-report=term-missing

# Генерація HTML звіту покриття
poetry run pytest --cov=src --cov-report=html

# Legacy тести (потребують запущеного сервера та бази даних)
poetry run python tests/test_basic.py
poetry run python tests/test_full_api.py
poetry run python tests/test_error_handling.py
poetry run python tests/test_with_client.py
poetry run python tests/simple_test.py

# Перевірка якості коду (весь pipeline)
poetry run black src/ && poetry run isort src/ && poetry run flake8 src/ --max-line-length=88
```

## Розробка

### Перед комітом
Рекомендується запускати перевірки якості коду:
```bash
# Форматування та перевірка
poetry run black src/
poetry run isort src/
poetry run flake8 src/ --max-line-length=88
```

### Корисні команди Poetry
```bash
# Показати інформацію про проект
poetry show

# Показати дерево залежностей  
poetry show --tree

# Додати нову залежність
poetry add package-name

# Додати dev залежність
poetry add --group dev package-name

# Експорт залежностей у requirements.txt (якщо потрібно)
poetry export -f requirements.txt --output requirements.txt
```

## Встановлення та запуск

### Передумови
- Python 3.8+
- PostgreSQL
- Poetry (для управління залежностями)

### Встановлення Poetry (якщо ще не встановлено)
```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Linux/Mac
curl -sSL https://install.python-poetry.org | python3 -
```

### Налаштування проекту

1. Клонуйте репозиторій:
```bash
git clone https://github.com/YOUR_USERNAME/goit-pythonweb-hw-08.git
cd goit-pythonweb-hw-08
```

2. Встановіть залежності через Poetry:
```bash
poetry install
```

3. Активуйте віртуальне середовище Poetry:
```bash
poetry shell
```

4. Запустіть PostgreSQL базу даних через Docker:
```bash
# Запустити PostgreSQL в Docker (потрібен Docker)
docker-compose up -d

# Або встановіть PostgreSQL локально і створіть:
# - базу даних: contacts_db
# - користувача: user з паролем: password
```

5. Налаштуйте змінні середовища:
```bash
cp .env.example .env
# Відредагуйте .env файл з вашими налаштуваннями БД
```

6. Запустіть додаток:
```bash
# Через Poetry
poetry run uvicorn main:app --reload
```

Додаток буде доступний за адресою: http://127.0.0.1:8000

**Швидкі посилання:**
- API документація (Swagger): http://127.0.0.1:8000/docs
- API документація (ReDoc): http://127.0.0.1:8000/redoc
- OpenAPI JSON (для Postman): http://127.0.0.1:8000/openapi.json

## API Документація

**Swagger UI**: http://127.0.0.1:8000/docs
**ReDoc**: http://127.0.0.1:8000/redoc

**Різниця між Swagger UI та ReDoc:**
- **Swagger UI** - інтерактивне тестування API прямо в браузері
- **ReDoc** - красива, зручна для читання документація з кращим дизайном

### Postman колекція

Для імпорту API в Postman використовуйте OpenAPI JSON схему:

**JSON Schema URL**: `http://127.0.0.1:8000/openapi.json`

**Як імпортувати в Postman:**
1. Запустіть сервер: `poetry run uvicorn main:app --host 127.0.0.1 --port 8000`
2. Відкрийте Postman
3. Натисніть "Import" → "Link"
4. Вставте URL: `http://127.0.0.1:8000/openapi.json`
5. Натисніть "Continue" → "Import"

Альтернативно, можете скопіювати JSON схему з браузера:
- Перейдіть на `http://127.0.0.1:8000/openapi.json`
- Скопіюйте весь JSON
- У Postman: "Import" → "Raw text" → вставте JSON

📋 **Детальний гід по Postman**: [postman-guide.md](postman-guide.md)

## Ендпоінти

### Контакти

- `POST /api/contacts/` - Створити новий контакт
- `GET /api/contacts/` - Отримати список контактів (з пагінацією та пошуком)
- `GET /api/contacts/{contact_id}` - Отримати контакт за ID
- `PUT /api/contacts/{contact_id}` - Оновити контакт
- `DELETE /api/contacts/{contact_id}` - Видалити контакт
- `GET /api/contacts/birthdays` - Отримати контакти з днями народження на наступні 7 днів

### Параметри пошуку

- `search` - Пошук за ім'ям, прізвищем або email
- `skip` - Пропустити N записів (для пагінації)
- `limit` - Обмежити кількість записів (max 100)

## Приклад використання

### Створення контакту

```bash
curl -X POST "http://127.0.0.1:8000/api/contacts/" \
-H "Content-Type: application/json" \
-d '{
  "first_name": "Іван",
  "last_name": "Петренко",
  "email": "ivan@example.com",
  "phone_number": "+380501234567",
  "birth_date": "1990-05-15",
  "additional_data": "Друг з університету"
}'
```

### Пошук контактів

```bash
curl "http://127.0.0.1:8000/api/contacts/?search=іван"
```

### Дні народження

```bash
curl "http://127.0.0.1:8000/api/contacts/birthdays"
```

## Технології

- **FastAPI** - Веб-фреймворк
- **SQLAlchemy** - ORM для роботи з базою даних
- **PostgreSQL** - База даних
- **Pydantic** - Валідація даних
- **Uvicorn** - ASGI сервер
- **Poetry** - Управління залежностями та пакетами
- **Black** - Форматування коду
- **isort** - Сортування імпортів
- **flake8** - Лінтинг коду

## Автор
Serhii Palamarchuk

Створено в рамках домашнього завдання GoIT Python Web Development

---

## Досягнення проекту
- ✅ **81% покриття коду** (177 тестів, всі проходять успішно)
- ✅ **100% покриття** ключових модулів (routes, schemas, models, exceptions)
- ✅ **Комплексна архітектура** з повним розділенням відповідальностей
- ✅ **Професійне тестування** з мокуванням та ізоляцією
- ✅ **Docker готовність** з автоматичною публікацією образів
- ✅ **Повна документація** API через Swagger/ReDoc
- ✅ **Rate limiting** та захист від зловживань
- ✅ **Email верифікація** та JWT аутентифікація
- ✅ **Інтеграція з Cloudinary** для завантаження зображень
