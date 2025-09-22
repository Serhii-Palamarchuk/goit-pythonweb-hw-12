from typing import Optional

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserCreate
from src.services.auth import get_password_hash


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    async def create_user(self, user: UserCreate) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def confirmed_email(self, email: str) -> None:
        """Mark user email as confirmed."""
        user = await self.get_user_by_email(email)
        if user:
            user.is_verified = True
            self.db.commit()

    async def update_avatar(self, email: str, url: str) -> User:
        """Update user avatar."""
        user = await self.get_user_by_email(email)
        if user:
            user.avatar = url
            self.db.commit()
            self.db.refresh(user)
        return user


def get_user_repo(db: Session) -> UserRepository:
    return UserRepository(db)
