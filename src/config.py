import os
from dotenv import load_dotenv

# Завантажуємо змінні з .env файлу
load_dotenv()


class Settings:
    def __init__(self):
        self.database_url: str = os.getenv(
            "DATABASE_URL", "postgresql://user:password@localhost:5432/contacts_db"
        )
        self.secret_key: str = os.getenv(
            "SECRET_KEY", "your-secret-key-change-this-in-production"
        )
        self.algorithm: str = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )

        # Email settings
        self.mail_username: str = os.getenv("MAIL_USERNAME", "")
        self.mail_password: str = os.getenv("MAIL_PASSWORD", "")
        self.mail_from: str = os.getenv("MAIL_FROM", "")
        self.mail_port: int = int(os.getenv("MAIL_PORT", "587"))
        self.mail_server: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")

        # Cloudinary settings
        self.cloudinary_name: str = os.getenv("CLOUDINARY_NAME", "")
        self.cloudinary_api_key: str = os.getenv("CLOUDINARY_API_KEY", "")
        self.cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET", "")

        # Redis settings for rate limiting
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

        # CORS settings
        default_origins = (
            "http://localhost:3000,http://localhost:8000,"
            "http://127.0.0.1:3000,http://127.0.0.1:8000"
        )
        self.cors_origins: list[str] = os.getenv("CORS_ORIGINS", default_origins).split(
            ","
        )


settings = Settings()
