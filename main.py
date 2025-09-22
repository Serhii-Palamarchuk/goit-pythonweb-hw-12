from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

from src.routes import contacts, auth
from src.config import settings


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Manage application lifespan events"""
    # Startup
    try:
        # Initialize FastAPI Limiter with Redis
        redis_client = redis.from_url(settings.redis_url)
        await FastAPILimiter.init(redis_client)
        print("Rate limiter initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize rate limiter: {e}")

    try:
        from src.database.models import Base
        from src.database.db import engine

        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except ImportError as e:
        print(f"Warning: Could not import database modules: {e}")
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("Please ensure PostgreSQL is running and configured correctly.")

    yield

    # Shutdown
    try:
        await FastAPILimiter.close()
        print("Rate limiter closed")
    except Exception:
        pass
    print("Application shutting down...")


app = FastAPI(
    title="Contacts API",
    description="REST API for managing contacts with authentication",
    version="1.0.0",
    lifespan=lifespan,
)  # Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Welcome to Contacts API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
