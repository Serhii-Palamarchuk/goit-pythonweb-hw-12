# 🚀 Quick Deploy Guide

## 🌐 Render.com (Recommended)

**1. Push to GitHub:**
```bash
git add . && git commit -m "Deploy" && git push
```

**2. Deploy on Render:**
- Go to [render.com](https://render.com) → Register with GitHub
- "New +" → "Web Service" → Select repo
- Render auto-uses `render.yaml` ✨

**3. Optional Environment Variables:**
```
# Email (for verification)
MAIL_USERNAME=your.email@gmail.com
MAIL_PASSWORD=app-password
MAIL_FROM=your.email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# Cloudinary (for avatars)
CLOUDINARY_NAME=your_name
CLOUDINARY_API_KEY=key
CLOUDINARY_API_SECRET=secret
```

**Done!** Your API: `https://your-app.onrender.com`

## 🧪 Test Endpoints:
- Health: `/health`
- Docs: `/docs`
- Register: `POST /api/auth/signup`

## 🐳 Docker Alternative:
```bash
docker-compose up --build
curl http://localhost:8000/health
```