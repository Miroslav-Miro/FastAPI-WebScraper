"""
Authentication service utilities for the Web Scraper API.

Includes functions for password hashing and verification,
JWT token creation, and current user retrieval from tokens.
"""

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
import os

from requests import Session

from app.core.database import get_db
from app.database.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain password against its hashed version.

    Args:
        plain (str): Plaintext password.
        hashed (str): Hashed password.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.

    Args:
        password (str): Plaintext password.

    Returns:
        str: Hashed password.
    """
    return pwd_context.hash(password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token with an expiration.

    Args:
        subject (str): The subject to encode in the token (usually username).
        expires_delta (timedelta | None): Optional custom expiration time.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = {"sub": subject}
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode JWT token, retrieve and return the current authenticated user.

    Args:
        token (str): JWT token from the Authorization header.
        db (Session): Database session.

    Returns:
        User: The authenticated User object.

    Raises:
        HTTPException: 401 Unauthorized if token is invalid or user not found.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if not username:
        raise HTTPException(401, "Invalid token")
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(401, "User not found")
    return user


def anonymous_only(user=Depends(get_current_user)):
    """
    Dependency to allow only anonymous (not logged in) users.

    Raises:
        HTTPException: 400 Bad Request if the user is already logged in.
    """
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You are already logged in."
        )
