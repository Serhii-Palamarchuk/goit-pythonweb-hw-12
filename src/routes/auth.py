from datetime import timedelta

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
    UploadFile,
    File,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.config import settings
from src.database.db import get_db
from src.database.models import User
from src.repository.users import get_user_repo
from src.schemas.users import UserCreate, UserResponse, Token, RequestEmail
from src.services.auth import (
    create_access_token,
    get_current_user,
    verify_password,
    get_email_from_token,
)
from src.services.email import send_verification_email_robust
from src.services.cloudinary import cloudinary_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Register a new user."""
    user_repo = get_user_repo(db)

    # Check if user already exists
    exist_user = await user_repo.get_user_by_email(body.email)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )

    exist_user = await user_repo.get_user_by_username(body.username)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
        )

    # Create new user
    new_user = await user_repo.create_user(body)

    # Send verification email
    background_tasks.add_task(
        send_verification_email_robust,
        new_user.email,
        new_user.username,
        str(request.base_url),
    )

    return new_user


@router.post("/login", response_model=Token)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate user and return access token."""
    user_repo = get_user_repo(db)

    # Get user by username
    user = await user_repo.get_user_by_username(body.username)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified. Please verify your account first.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """Confirm user email."""
    email = await get_email_from_token(token)
    user_repo = get_user_repo(db)
    user = await user_repo.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.is_verified:
        return {"message": "Your email is already confirmed"}
    await user_repo.confirmed_email(email)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Request email verification."""
    user_repo = get_user_repo(db)
    user = await user_repo.get_user_by_email(body.email)

    if user and not user.is_verified:
        background_tasks.add_task(
            send_verification_email_robust,
            user.email,
            user.username,
            str(request.base_url),
        )
    return {"message": "Check your email for confirmation."}


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information. Limited to 10 requests per minute."""
    return current_user


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user avatar."""
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG are allowed.",
        )

    # Upload to Cloudinary
    avatar_url = cloudinary_service.upload_image(file, folder="avatars")
    if not avatar_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Could not upload avatar"
        )

    # Update user avatar in database
    user_repo = get_user_repo(db)
    user = await user_repo.update_avatar(current_user.email, avatar_url)
    return user
