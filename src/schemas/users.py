"""
User schemas for request/response validation.

This module contains Pydantic models for user-related operations
including registration, authentication, and password management.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=6, max_length=255)


class UserResponse(UserBase):
    """Schema for user response data."""

    id: int
    is_verified: bool
    avatar: Optional[str] = None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for user profile updates."""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token payload data."""

    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str


class RequestEmail(BaseModel):
    """Schema for email verification request."""

    email: EmailStr


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""

    email: EmailStr


class PasswordReset(BaseModel):
    """Schema for password reset with token."""

    token: str
    new_password: str = Field(..., min_length=6, max_length=255)
