# JWT Refresh Token Implementation

## 🔄 **Механізм оновлення токенів доступу**

Наша система тепер підтримує безпечний механізм оновлення токенів доступу за допомогою `refresh_token`.

### 🎯 **Основні особливості:**

1. **Подвійна система токенів:**
   - `access_token` - короткотерміновий (30 хвилин)
   - `refresh_token` - довготерміновий (7 днів)

2. **Безпечність:**
   - Різні scope для access і refresh токенів
   - Валідація типу токену при використанні
   - Автоматичне оновлення обох токенів

### 📋 **API Endpoints:**

#### 1. **POST /auth/login** (оновлено)
Тепер повертає обидва токени:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### 2. **POST /auth/refresh** (новий)
Оновлює токени за допомогою refresh_token:

**Request:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access_token": "NEW_ACCESS_TOKEN_HERE",
  "refresh_token": "NEW_REFRESH_TOKEN_HERE", 
  "token_type": "bearer"
}
```

### 🛡️ **Безпека:**

1. **Scope валідація** - access токен не може використовуватися як refresh
2. **Автоматичне оновлення** - при refresh видаються нові обидва токени
3. **Різні терміни дії** - access (30 хв) vs refresh (7 днів)
4. **JWT підпис** - всі токени підписані секретним ключем

### 💻 **Приклад використання в клієнті:**

```javascript
// 1. Логін і отримання токенів
const loginResponse = await fetch('/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=user&password=pass'
});
const { access_token, refresh_token } = await loginResponse.json();

// 2. Використання access_token для API запитів
const apiResponse = await fetch('/contacts/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});

// 3. Оновлення токенів коли access_token закінчується
const refreshResponse = await fetch('/auth/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh_token })
});
const newTokens = await refreshResponse.json();
```

### ⚠️ **Важливі моменти:**

1. **Зберігання токенів:**
   - `access_token` - в пам'яті (sessionStorage)
   - `refresh_token` - в безпечному cookie (httpOnly)

2. **Обробка помилок:**
   - `401 Unauthorized` - токен недійсний/закінчився
   - `422 Unprocessable Entity` - неправильний формат токену

3. **Автоматизація:**
   - Клієнт повинен автоматично оновлювати токени
   - При помилці refresh - перенаправлення на логін

### 🧪 **Тестування:**

```bash
# Запуск тестів refresh токенів
poetry run pytest tests/test_refresh_tokens.py -v
```

**Всі тести пройшли успішно:** ✅
- Створення refresh токенів
- Валідація токенів  
- Різні scope для access/refresh
- Різні терміни дії
- API схеми

## 🎉 **Результат:**

JWT токени з механізмом refresh **ПОВНІСТЮ РЕАЛІЗОВАНІ** відповідно до вимог домашки HW-12!