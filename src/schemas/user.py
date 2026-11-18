"""Pydantic schemas for User validation and serialization (M2).
"""

from datetime import datetime
import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# Regular expression for RFC 5322 compliant email validation
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

# Regular expression for username validation (alphanumeric, underscores, hyphens)
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]+$")

# Special characters allowed in passwords
SPECIAL_CHARS_REGEX = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]")


def validate_email_format(email: str) -> str:
    """Validate and normalize email string."""
    if not isinstance(email, str):
        raise ValueError("Email must be a valid string.")
    
    normalized = email.strip().lower()
    if not normalized:
        raise ValueError("Email cannot be empty.")
    
    if len(normalized) > 255:
        raise ValueError("Email address cannot exceed 255 characters.")
    
    if not EMAIL_REGEX.match(normalized):
        raise ValueError("Invalid email address format.")
    
    return normalized


def validate_username_format(username: str) -> str:
    """Validate and sanitize username string."""
    if not isinstance(username, str):
        raise ValueError("Username must be a valid string.")
    
    cleaned = username.strip()
    if len(cleaned) < 3:
        raise ValueError("Username must be at least 3 characters long.")
    
    if len(cleaned) > 50:
        raise ValueError("Username cannot exceed 50 characters.")
    
    if not USERNAME_REGEX.match(cleaned):
        raise ValueError(
            "Username can only contain alphanumeric characters, underscores, and hyphens."
        )
    
    return cleaned


def validate_password_strength(password: str) -> str:
    """Validate password strength according to security requirements.

    Requirements:
    - Minimum length: 8 characters
    - Maximum length: 128 characters
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one numerical digit (0-9)
    - At least one special symbol (!@#$%^&*...)
    """
    if not isinstance(password, str):
        raise ValueError("Password must be a valid string.")
    
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    
    if len(password) > 128:
        raise ValueError("Password cannot exceed 128 characters.")
    
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")
    
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")
    
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit.")
    
    if not SPECIAL_CHARS_REGEX.search(password):
        raise ValueError(
            "Password must contain at least one special character (!@#$%^&*...)."
        )
    
    return password


class UserBase(BaseModel):
    """Base schema for shared user attributes."""

    email: str = Field(
        ...,
        description="User email address (automatically normalized to lowercase).",
        examples=["user@example.com"],
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username for account identification.",
        examples=["john_doe"],
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="User's full name (optional).",
        examples=["John Doe"],
    )
    is_active: Optional[bool] = Field(
        default=True,
        description="Whether the user account is active.",
    )

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return validate_email_format(v)

    @field_validator("username")
    @classmethod
    def check_username(cls, v: str) -> str:
        return validate_username_format(v)

    @field_validator("full_name")
    @classmethod
    def check_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            return cleaned if cleaned else None
        return None


class UserCreate(UserBase):
    """Schema for registering a new user."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Strong user password with complexity requirements.",
        examples=["SecurePass123!"],
    )

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UserUpdate(BaseModel):
    """Schema for updating an existing user's profile."""

    email: Optional[str] = Field(default=None, description="New email address.")
    username: Optional[str] = Field(default=None, description="New username.")
    full_name: Optional[str] = Field(default=None, description="New full name.")
    password: Optional[str] = Field(
        default=None,
        description="New password (must meet complexity requirements).",
    )
    is_active: Optional[bool] = Field(default=None, description="Active status.")

    @field_validator("email")
    @classmethod
    def check_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_email_format(v)
        return None

    @field_validator("username")
    @classmethod
    def check_username(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_username_format(v)
        return None

    @field_validator("password")
    @classmethod
    def check_password(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_password_strength(v)
        return None

    @field_validator("full_name")
    @classmethod
    def check_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            return cleaned if cleaned else None
        return None


class UserResponse(BaseModel):
    """Schema for safe public serialization of user data.

    Never exposes hashed_password or plain text passwords.
    """

    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login credentials."""

    username_or_email: str = Field(
        ...,
        description="Username or email address of the account.",
    )
    password: str = Field(
        ...,
        description="Account password.",
    )


class Token(BaseModel):
    """Bearer token response schema."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Payload stored inside JWT token."""

    user_id: Optional[int] = None
    username: Optional[str] = None
