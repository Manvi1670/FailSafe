# ============================================================
# auth.py — Password hashing + JWT token logic
# ============================================================
# This file does NOT define any endpoints. It only contains
# the helper functions that the router files will call.
# Two jobs:
#   1. Hash passwords before storing (passlib/bcrypt)
#   2. Create and verify JWT tokens (python-jose)

import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

# --- Password hashing setup ---
# bcrypt is the industry standard for storing passwords safely.
# Even if someone steals your database, they cannot reverse a
# bcrypt hash back into the original password.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- JWT setup ---
# OAuth2PasswordBearer tells FastAPI which URL to direct users
# to when they need to log in. tokenUrl must match the login
# endpoint we'll create in routers/auth_router.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY  = os.getenv("SECRET_KEY", "fallback_secret")
ALGORITHM   = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


# ---- Password utilities ----

def hash_password(plain_password: str) -> str:
    """Converts plain text password into a bcrypt hash for storage."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain text password matches the stored hash.
    Used during login — we never store or compare plain passwords.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ---- JWT utilities ----

def create_access_token(data: dict,
                         expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT token containing the user's info.
    The token expires after ACCESS_TOKEN_EXPIRE_MINUTES (60 mins).
    After expiry the user must log in again — this is the security boundary.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[str]:
    """
    Decodes a JWT token and returns the user's email (called 'sub').
    Returns None if the token is expired or tampered with.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None


# ---- FastAPI dependency: get current logged-in user ----

def get_current_user(token: str = Depends(oauth2_scheme),
                      db: Session = Depends(get_db)) -> User:
    """
    This is a FastAPI 'dependency' — you add it to any endpoint
    that requires the user to be logged in. FastAPI automatically
    extracts the JWT token from the request header, calls this
    function, and passes the returned User object to your endpoint.

    If the token is missing, expired, or fake — it raises a 401
    Unauthorized error and the endpoint never runs.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = verify_token(token)
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_faculty(current_user: User = Depends(get_current_user)) -> User:
    """
    Extends get_current_user — only allows faculty OR hod roles.
    Used on endpoints that any logged-in user can access.
    """
    if current_user.role not in ["faculty", "hod"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_current_hod(current_user: User = Depends(get_current_user)) -> User:
    """
    Extends get_current_user — only allows hod role.
    Used on HOD-only endpoints like school-wide dashboard.
    """
    if current_user.role != "hod":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HOD access required"
        )
    return current_user