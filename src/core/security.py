"""Security utilities for password hashing, verification, and JWT handling.
Part of M2 Authentication Module.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import hashlib
import secrets

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    HAS_PASSLIB = True
except ImportError:  # pragma: no cover
    pwd_context = None
    HAS_PASSLIB = False

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings

# OAuth2 scheme for extracting Bearer tokens from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a hashed password.

    Supports passlib bcrypt hashes and PBKDF2-SHA256 fallback hashes.
    """
    if not plain_password or not hashed_password:
        return False

    # Check for PBKDF2-SHA256 fallback format
    if hashed_password.startswith("pbkdf2_sha256$"):
        try:
            parts = hashed_password.split("$")
            if len(parts) != 3:
                return False
            salt = parts[1]
            stored_hash = parts[2]
            computed_hash = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                100000,
            ).hex()
            return secrets.compare_digest(computed_hash, stored_hash)
        except Exception:
            return False

    # Standard passlib verification
    if HAS_PASSLIB and pwd_context is not None:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False

    return False


def get_password_hash(password: str) -> str:
    """Generate a secure cryptographic hash for a plain-text password.

    Uses bcrypt via passlib when available, or PBKDF2-SHA256 with 100,000 rounds.
    """
    if not password:
        raise ValueError("Password cannot be empty.")

    if HAS_PASSLIB and pwd_context is not None:
        try:
            return pwd_context.hash(password)
        except Exception:  # pragma: no cover
            pass

    # Secure fallback using Python standard library hashlib
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()
    return f"pbkdf2_sha256${salt}${dk}"


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token containing subject data and expiration."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """Decode and validate a JWT access token.

    Returns the payload dictionary if valid, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except jwt.PyJWTError:
        return None


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """FastAPI dependency that extracts and validates the current user ID from a JWT.

    Raises HTTP 401 if the token is missing, invalid, expired, or malformed.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception

    return user_id
