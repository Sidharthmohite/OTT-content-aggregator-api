"""User service module handling business logic, authentication, and duplicate handling (M2).
"""

from typing import Any, Optional
from datetime import datetime, timezone

try:
    from sqlalchemy.orm import Session
    from sqlalchemy.exc import IntegrityError
    HAS_SQLALCHEMY = True
except ImportError:  # pragma: no cover
    HAS_SQLALCHEMY = False
    Session = Any
    IntegrityError = Exception

from src.core.security import get_password_hash, verify_password
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate


class DuplicateEmailError(Exception):
    """Raised when an email address is already registered."""
    pass


class DuplicateUsernameError(Exception):
    """Raised when a username is already taken."""
    pass


class UserNotFoundError(Exception):
    """Raised when a user is not found in the database."""
    pass


# Backward compatibility alias
UserAlreadyExistsError = DuplicateEmailError
UsernameAlreadyExistsError = DuplicateUsernameError


class UserService:
    """Service providing user management, duplicate handling, and authentication."""

    @staticmethod
    def get_user_by_id(db: Any, user_id: int) -> Optional[User]:
        """Retrieve a user by their unique primary key ID."""
        if hasattr(db, "query"):
            return db.query(User).filter(User.id == user_id).first()
        elif hasattr(db, "get"):  # in-memory store mock
            return db.get(user_id)
        return None

    @staticmethod
    def get_user_by_email(db: Any, email: str) -> Optional[User]:
        """Retrieve a user by normalized lowercase email address."""
        normalized_email = email.strip().lower()
        if hasattr(db, "query"):
            return db.query(User).filter(User.email == normalized_email).first()
        elif hasattr(db, "find_by_email"):
            return db.find_by_email(normalized_email)
        return None

    @staticmethod
    def get_user_by_username(db: Any, username: str) -> Optional[User]:
        """Retrieve a user by unique username."""
        cleaned_username = username.strip()
        if hasattr(db, "query"):
            return db.query(User).filter(User.username == cleaned_username).first()
        elif hasattr(db, "find_by_username"):
            return db.find_by_username(cleaned_username)
        return None

    @classmethod
    def create_user(cls, db: Any, user_create: UserCreate) -> User:
        """Create a new user with email and field validation, duplicate checks, and password hashing.

        Raises:
            DuplicateEmailError: If the email is already registered.
            DuplicateUsernameError: If the username is already taken.
        """
        # 1. Duplicate email check
        existing_email = cls.get_user_by_email(db, user_create.email)
        if existing_email:
            raise DuplicateEmailError(
                f"User with email '{user_create.email}' is already registered."
            )

        # 2. Duplicate username check
        existing_username = cls.get_user_by_username(db, user_create.username)
        if existing_username:
            raise DuplicateUsernameError(
                f"Username '{user_create.username}' is already taken."
            )

        # 3. Hash user password securely
        hashed_password = get_password_hash(user_create.password)

        # 4. Instantiate model
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            is_active=user_create.is_active if user_create.is_active is not None else True,
        )

        # 5. Commit with IntegrityError safety net
        if hasattr(db, "add") and hasattr(db, "commit"):
            try:
                db.add(db_user)
                db.commit()
                if hasattr(db, "refresh"):
                    db.refresh(db_user)
            except IntegrityError as exc:
                db.rollback()
                error_msg = str(exc).lower()
                if "email" in error_msg:
                    raise DuplicateEmailError(
                        f"User with email '{user_create.email}' is already registered."
                    ) from exc
                elif "username" in error_msg:
                    raise DuplicateUsernameError(
                        f"Username '{user_create.username}' is already taken."
                    ) from exc
                else:
                    raise DuplicateEmailError(
                        "Registration failed due to duplicate database constraint."
                    ) from exc
        elif hasattr(db, "save"):
            db.save(db_user)

        return db_user

    @classmethod
    def update_user(cls, db: Any, user_id: int, user_update: UserUpdate) -> User:
        """Update an existing user's profile with duplicate conflict checks.

        Raises:
            UserNotFoundError: If the user does not exist.
            DuplicateEmailError: If the new email is already taken by another user.
            DuplicateUsernameError: If the new username is already taken by another user.
        """
        user = cls.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found.")

        # Email update duplicate verification
        if user_update.email is not None and user_update.email != user.email:
            existing = cls.get_user_by_email(db, user_update.email)
            if existing and existing.id != user_id:
                raise DuplicateEmailError(
                    f"Email '{user_update.email}' is already registered to another account."
                )
            user.email = user_update.email

        # Username update duplicate verification
        if user_update.username is not None and user_update.username != user.username:
            existing = cls.get_user_by_username(db, user_update.username)
            if existing and existing.id != user_id:
                raise DuplicateUsernameError(
                    f"Username '{user_update.username}' is already taken by another user."
                )
            user.username = user_update.username

        # Password update with re-hashing
        if user_update.password is not None:
            user.hashed_password = get_password_hash(user_update.password)

        if user_update.full_name is not None:
            user.full_name = user_update.full_name

        if user_update.is_active is not None:
            user.is_active = user_update.is_active

        if hasattr(user, "updated_at"):
            user.updated_at = datetime.now(timezone.utc)

        if hasattr(db, "commit"):
            try:
                db.commit()
                if hasattr(db, "refresh"):
                    db.refresh(user)
            except IntegrityError as exc:
                db.rollback()
                raise DuplicateEmailError("Failed to update user due to duplicate value.") from exc
        elif hasattr(db, "save"):
            db.save(user)

        return user

    @classmethod
    def authenticate_user(
        cls, db: Any, username_or_email: str, password: str
    ) -> Optional[User]:
        """Authenticate a user by email or username and verify password."""
        user = cls.get_user_by_email(db, username_or_email)
        if not user:
            user = cls.get_user_by_username(db, username_or_email)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user
