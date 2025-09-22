"""
Authentication service module.

This module provides authentication and authorization functionality
including password hashing, JWT token management, and user caching.
"""

from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.config import settings
from src.database.db import get_db
from src.database.models import User, UserRole
from src.schemas.users import TokenData
from src.services.redis_cache import redis_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password (str): Plain text password
        hashed_password (str): Hashed password from database

    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password (str): Plain text password

    Returns:
        str: Hashed password
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token.

    Args:
        data (dict): Data to encode in the token
        expires_delta (Optional[timedelta]): Token expiration time

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def create_email_token(data: dict):
    """
    Create a JWT token for email verification.

    Args:
        data (dict): Data to encode in the token

    Returns:
        str: Encoded JWT token for email verification
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return token


def create_password_reset_token(data: dict):
    """
    Create a JWT token for password reset.

    Args:
        data (dict): Data to encode in the token

    Returns:
        str: Encoded JWT token for password reset
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    to_encode.update(
        {"iat": datetime.utcnow(), "exp": expire, "scope": "password_reset"}
    )
    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return token


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Get the current authenticated user with Redis caching.

    This function first checks Redis cache for user data,
    and only queries the database if cache miss occurs.

    Args:
        token (str): JWT access token
        db (Session): Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(username=email)
    except JWTError:
        raise credentials_exception

    # Try to get user from cache first
    cached_user_data = await redis_service.get_cached_user(email)
    if cached_user_data:
        # Reconstruct User object from cached data
        user = User()
        user.id = cached_user_data["id"]
        user.username = cached_user_data["username"]
        user.email = cached_user_data["email"]
        user.hashed_password = cached_user_data["hashed_password"]
        user.is_verified = cached_user_data["is_verified"]
        user.avatar = cached_user_data["avatar"]
        user.role = UserRole(cached_user_data["role"])

        # Parse datetime strings back to datetime objects if present
        if cached_user_data["created_at"]:
            user.created_at = datetime.fromisoformat(cached_user_data["created_at"])
        if cached_user_data["updated_at"]:
            user.updated_at = datetime.fromisoformat(cached_user_data["updated_at"])

        return user

    # Cache miss - query database
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    # Cache the user for future requests
    await redis_service.cache_user(user)

    return user


async def get_email_from_token(token: str):
    """
    Get email from verification token.

    Args:
        token (str): JWT token

    Returns:
        str: Email address from token

    Raises:
        HTTPException: If token is invalid or has wrong scope
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        if payload["scope"] == "email_token":
            email = payload["sub"]
            return email
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid token"
        )


async def verify_password_reset_token(token: str):
    """
    Verify password reset token and extract email.

    Args:
        token (str): Password reset token

    Returns:
        str: Email address from token

    Raises:
        HTTPException: If token is invalid or has wrong scope
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        if payload["scope"] == "password_reset":
            email = payload["sub"]
            return email
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid token"
        )


def check_admin_role(current_user: User = Depends(get_current_user)):
    """
    Check if current user has admin role.

    Args:
        current_user (User): Current authenticated user

    Returns:
        User: Current user if admin

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user
