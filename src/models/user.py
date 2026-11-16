"""SQLAlchemy database model for User accounts (M2).
"""

from datetime import datetime, timezone
from typing import Optional

try:
    from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
    from src.core.database import Base
    HAS_SQLALCHEMY = True
except ImportError:  # pragma: no cover
    HAS_SQLALCHEMY = False
    Base = object


if HAS_SQLALCHEMY and Base is not object:
    class User(Base):
        """User database model representing registered user accounts."""

        __tablename__ = "users"

        id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        email = Column(String(255), unique=True, index=True, nullable=False)
        username = Column(String(50), unique=True, index=True, nullable=False)
        hashed_password = Column(String(255), nullable=False)
        full_name = Column(String(100), nullable=True)
        is_active = Column(Boolean, default=True, nullable=False)
        is_superuser = Column(Boolean, default=False, nullable=False)
        created_at = Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
        updated_at = Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )

        def __repr__(self) -> str:
            return (
                f"<User(id={self.id}, username='{self.username}', "
                f"email='{self.email}', is_active={self.is_active})>"
            )

else:  # pragma: no cover
    # Standalone mock model for environments without SQLAlchemy installed
    class User:
        """Mock User model matching SQLAlchemy definition for lightweight testing."""

        __tablename__ = "users"

        def __init__(
            self,
            id: Optional[int] = None,
            email: str = "",
            username: str = "",
            hashed_password: str = "",
            full_name: Optional[str] = None,
            is_active: bool = True,
            is_superuser: bool = False,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
        ):
            self.id = id
            self.email = email
            self.username = username
            self.hashed_password = hashed_password
            self.full_name = full_name
            self.is_active = is_active
            self.is_superuser = is_superuser
            self.created_at = created_at or datetime.now(timezone.utc)
            self.updated_at = updated_at or datetime.now(timezone.utc)

        def __repr__(self) -> str:
            return (
                f"<User(id={self.id}, username='{self.username}', "
                f"email='{self.email}', is_active={self.is_active})>"
            )
