import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, validator


class ContactBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: str
    phone_number: str = Field(..., min_length=1, max_length=20)
    birth_date: date
    additional_data: Optional[str] = None

    @validator("email")
    def validate_email(cls, v):
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format")
        return v


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = None
    phone_number: Optional[str] = Field(None, min_length=1, max_length=20)
    birth_date: Optional[date] = None
    additional_data: Optional[str] = None

    @validator("email")
    def validate_email(cls, v):
        if v and not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format")
        return v


class ContactResponse(ContactBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
