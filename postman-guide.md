# Postman Collection для Contacts API

## Автоматичний імпорт (рекомендується)

1. Запустіть сервер:
   ```bash
   poetry run uvicorn main:app --host 127.0.0.1 --port 8000
   ```

2. Імпортуйте колекцію в Postman:
   - Відкрийте Postman
   - Натисніть "Import" → "Link" 
   - Вставте URL: `http://127.0.0.1:8000/openapi.json`
   - Натисніть "Continue" → "Import"

## Альтернативи Postman

### Інтерактивна документація
- **Swagger UI**: `http://127.0.0.1:8000/docs` - інтерактивне тестування
- **ReDoc**: `http://127.0.0.1:8000/redoc` - красива документація

## Основні запити для ручного тестування

### 1. Створення контакту
```
POST http://127.0.0.1:8000/api/contacts/
Content-Type: application/json

{
  "first_name": "Іван",
  "last_name": "Петренко",
  "email": "ivan@example.com",
  "phone_number": "+380501234567",
  "birth_date": "1990-05-15",
  "additional_data": "Друг з університету"
}
```

### 2. Отримання всіх контактів
```
GET http://127.0.0.1:8000/api/contacts/
```

### 3. Пошук контактів
```
GET http://127.0.0.1:8000/api/contacts/?search=Іван
```

### 4. Отримання контакту за ID
```
GET http://127.0.0.1:8000/api/contacts/1
```

### 5. Оновлення контакту
```
PUT http://127.0.0.1:8000/api/contacts/1
Content-Type: application/json

{
  "first_name": "Іван",
  "last_name": "Іваненко"
}
```

### 6. Видалення контакту
```
DELETE http://127.0.0.1:8000/api/contacts/1
```

### 7. Контакти з днями народження
```
GET http://127.0.0.1:8000/api/contacts/birthdays
```

## Змінні для Postman

Створіть environment з змінними:
- `base_url`: `http://127.0.0.1:8000`
- `api_prefix`: `/api`

Тоді запити можна записувати як:
```
{{base_url}}{{api_prefix}}/contacts/
```

## Тестування помилок

### Дублікат email (400)
```
POST http://127.0.0.1:8000/api/contacts/
Content-Type: application/json

{
  "first_name": "Тест",
  "last_name": "Користувач",
  "email": "ivan@example.com",
  "phone_number": "+380123456789",
  "birth_date": "1990-01-01"
}
```

### Неіснуючий контакт (404)
```
GET http://127.0.0.1:8000/api/contacts/999
```