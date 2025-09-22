# 🚀 Деплой Contacts API

## ✅ Готово до розгортання!

Проект повністю налаштований з усіма необхідними файлами.

## 🌐 Рекомендований спосіб: Render.com

### Переваги:
- 🆓 Безкоштовний план
- 🔄 Автодеплой з GitHub  
- 🗄️ Вбудовані PostgreSQL і Redis
- ⚡ Автоматичне налаштування через `render.yaml`

### Швидкий деплой:

**1. Завантажте на GitHub:**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

**2. Деплой на Render:**
- Йдіть на [render.com](https://render.com)
- Зареєструйтеся через GitHub
- "New +" → "Web Service" → оберіть репозиторій
- Render автоматично використає `render.yaml`! ✨

**3. Налаштуйте email (опціонально):**
```
MAIL_USERNAME=ваш.email@gmail.com
MAIL_PASSWORD=пароль-програми-gmail
MAIL_FROM=ваш.email@gmail.com
```

**4. Cloudinary для аватарів (опціонально):**
```
CLOUDINARY_NAME=ваше_ім'я
CLOUDINARY_API_KEY=ключ
CLOUDINARY_API_SECRET=секрет
```

**Готово!** Ваш API буде доступний за адресою:
`https://ваше-ім'я.onrender.com`

## 🧪 Перевірка деплою:

- Health check: `/health`
- API документація: `/docs` 
- Реєстрація: `POST /auth/signup`
- Логін: `POST /auth/login`

## 🐳 Альтернатива: Docker

```bash
# Локальний тест
docker-compose up --build

# Перевірка
curl http://localhost:8000/health
```

## 🔧 Що включено:

- ✅ JWT auth з refresh токенами
- ✅ Redis кешування  
- ✅ PostgreSQL база даних
- ✅ Email верифікація
- ✅ Завантаження аватарів
- ✅ Rate limiting
- ✅ Health monitoring
- ✅ Role-based доступ

**Все готово для продакшену!** 🎯