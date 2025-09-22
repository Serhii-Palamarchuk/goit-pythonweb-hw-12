# Contacts API - Фінальне домашнє завдання

Це повнофункціональний REST API для управління контактами, створений з використанням FastAPI та SQLAlchemy.

## 🎯 Реалізовані функції

### ✅ Основні вимоги (100 балів)

1. **📚 Документація Sphinx (15 балів)**
   - Додано docstrings до всіх основних функцій і методів
   - Налаштована генерація документації через Sphinx
   - Файли документації розташовані в папці `docs/`

2. **🧪 Модульне тестування (15 балів)**
   - Повне покриття тестами модулів репозиторію
   - Тести для користувачів (`tests/test_repository_users.py`)
   - Тести для контактів (`tests/test_repository_contacts.py`)

3. **🔄 Інтеграційне тестування (20 балів)**
   - Повне покриття API маршрутів
   - Тести автентифікації та авторизації
   - Тести CRUD операцій (`tests/test_integration_contacts.py`)

4. **📊 Покриття тестами >75% (10 балів)**
   - Налаштовано pytest-cov
   - Конфігурація в `pytest.ini`
   - Автоматична перевірка покриття

5. **⚡ Кешування Redis (15 балів)**
   - Реалізовано кешування користувачів
   - Функція `get_current_user` використовує кеш
   - Служба Redis Cache (`src/services/redis_cache.py`)

6. **🔐 Скидання пароля (15 балів)**
   - Безпечний механізм через email
   - JWT токени з обмеженим терміном дії
   - Маршрути: `/auth/request-password-reset`, `/auth/reset-password`

7. **👮 Ролі користувачів (10 балів)**
   - Ролі USER та ADMIN
   - Контроль доступу до функцій
   - Лише адміністратори можуть змінювати свій аватар

### 🛠 Технічні особливості

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL + SQLAlchemy 2.0
- **Cache**: Redis для кешування користувачів
- **Authentication**: JWT токени з bcrypt
- **Email**: FastAPI-Mail для відправки emails
- **File Upload**: Cloudinary для аватарів
- **Rate Limiting**: FastAPI-Limiter з Redis
- **Testing**: pytest + pytest-asyncio + pytest-cov
- **Documentation**: Sphinx з RTD theme
- **Containerization**: Docker + Docker Compose

## 🚀 Швидкий старт

### 1. Клонування репозиторію

```bash
git clone https://github.com/yourusername/goit-pythonweb-hw-12.git
cd goit-pythonweb-hw-12
```

### 2. Встановлення залежностей

```bash
# З Poetry
poetry install

# Або з pip
pip install -r requirements.txt
```

### 3. Налаштування середовища

```bash
cp .env.example .env
# Відредагуйте .env файл з вашими налаштуваннями
```

### 4. Запуск з Docker

```bash
docker-compose up -d
```

### 5. Запуск без Docker

```bash
# Запустіть PostgreSQL та Redis окремо
# Потім запустіть додаток
poetry run uvicorn main:app --reload
```

## 📖 Документація API

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Sphinx docs**: Генеруйте командою `sphinx-build -b html docs docs/_build`

## 🧪 Тестування

### Запуск всіх тестів

```bash
poetry run pytest
```

### Тести з покриттям

```bash
poetry run pytest --cov=src --cov-report=html
```

### Конкретні типи тестів

```bash
# Модульні тести
poetry run pytest tests/test_repository_*.py

# Інтеграційні тести
poetry run pytest tests/test_integration_*.py
```

## 📚 Генерація документації Sphinx

```bash
cd docs
sphinx-build -b html . _build/html
```

## 🔑 API Ендпоінти

### Автентифікація
- `POST /auth/signup` - Реєстрація користувача
- `POST /auth/login` - Вхід в систему
- `GET /auth/confirmed_email/{token}` - Підтвердження email
- `POST /auth/request_email` - Повторна відправка підтвердження
- `POST /auth/request-password-reset` - Запит скидання пароля
- `POST /auth/reset-password` - Скидання пароля за токеном
- `GET /auth/me` - Поточний користувач
- `PATCH /auth/avatar` - Оновлення аватара (лише для админів)

### Контакти
- `GET /contacts/` - Список контактів (з пошуком і пагінацією)
- `POST /contacts/` - Створення контакту
- `GET /contacts/{id}` - Отримання контакту
- `PUT /contacts/{id}` - Оновлення контакту
- `DELETE /contacts/{id}` - Видалення контакту
- `GET /contacts/birthdays` - Найближчі дні народження

## 🗂 Структура проекту

```
├── src/
│   ├── database/           # Моделі БД та підключення
│   ├── repository/         # Репозиторії для роботи з БД
│   ├── routes/            # API маршрути
│   ├── schemas/           # Pydantic схеми
│   ├── services/          # Бізнес логіка та сервіси
│   └── config.py          # Конфігурація додатку
├── tests/                 # Тести
├── docs/                  # Документація Sphinx
├── docker-compose.yml     # Docker Compose конфігурація
└── main.py               # Точка входу додатку
```

## 🔒 Безпека

- Паролі хешуються за допомогою bcrypt
- JWT токени з обмеженим терміном дії
- Rate limiting на API ендпоінти
- Валідація та санітизація вхідних даних
- CORS захист
- Безпечне скидання паролів через email

## 📊 Моніторинг та логування

- Детальне логування операцій
- Кешування для покращення продуктивності
- Метрики Redis для моніторингу кешу
- Обробка помилок та винятків

## 🤝 Внесок у розробку

1. Fork репозиторію
2. Створіть feature гілку
3. Зробіть зміни
4. Додайте тести
5. Створіть Pull Request

## 📝 Ліцензія

MIT License - дивіться файл LICENSE для деталей.

---

**Розробник**: Сергій Паламарчук
**Курс**: FullStack Web Development with Python  
**Завдання**: Фінальне домашнє завдання