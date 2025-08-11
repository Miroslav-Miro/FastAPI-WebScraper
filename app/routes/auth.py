"""
Authentication routes for the Web Scraper API.

Includes endpoints for user registration and login,
handling password hashing, user verification, and JWT token creation.
"""

from fastapi import APIRouter, Depends, Cookie, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.database.models import User
from app.schemas import UserCreate, Token, UserRead
from app.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from jose import JWTError, jwt
from app.schemas import TokenData
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    - Checks if the username is already taken.
    - Hashes the user's password.
    - Creates and commits a new User record.

    Args:
        user (UserCreate): Incoming user registration data.
        db (Session): SQLAlchemy DB session (injected).

    Returns:
        UserRead: Created user data (excluding sensitive info).

    Raises:
        HTTPException: 400 if username is already taken.
    """
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    return db_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT access token.

    - Verifies username and password.
    - Raises 401 if authentication fails.
    - Returns access token and token type on success.

    Args:
        form_data (OAuth2PasswordRequestForm): OAuth2 form data from request.
        db (Session): SQLAlchemy DB session (injected).

    Returns:
        Token: JWT access token and token type.

    Raises:
        HTTPException: 401 Unauthorized if credentials are invalid.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh")
def refresh_access_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias="refresh_token")
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = verify_refresh_token(refresh_token)
        username = payload.get("sub")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired. Please log in again.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = create_access_token(username)

    new_refresh = create_refresh_token(username)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/",
    )

    return {"access_token": new_access, "token_type": "bearer"}
