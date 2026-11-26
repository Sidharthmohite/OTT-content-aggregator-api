
"""User service module handling business logic, authentication, and duplicate handling (M2)."""

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


# Backward compatibility aliases
UserAlreadyExistsError = DuplicateEmailError
UsernameAlreadyExistsError = DuplicateUsernameError


class UserService:
    """Service providing user management, duplicate handling, and authentication."""

    # --------------------------------------------------
    # NORMALIZATION HELPERS
    # --------------------------------------------------

    @staticmethod
    def _normalize_email(email: str) -> str:
        """Normalize email by removing spaces and converting to lowercase."""
        return email.strip().lower()

    @staticmethod
    def _normalize_username(username: str) -> str:
        """Normalize username by removing surrounding spaces."""
        return username.strip()

    @staticmethod
    def _get_integrity_error_field(exc: Exception) -> Optional[str]:
        """Identify whether an integrity error relates to email or username."""
        original_error = getattr(exc, "orig", None)
        error_text = str(original_error or exc).lower()

        # Check the database error message
        if "email" in error_text:
            return "email"

        if "username" in error_text:
            return "username"

        # Check named constraints, if available
        diagnostic = getattr(original_error, "diag", None)
        constraint_name = getattr(diagnostic, "constraint_name", None)

        if constraint_name:
            constraint_name = constraint_name.lower()

            if "email" in constraint_name:
                return "email"

            if "username" in constraint_name:
                return "username"

        return None

    # --------------------------------------------------
    # USER RETRIEVAL
    # --------------------------------------------------

    @staticmethod
    def get_user_by_id(db: Any, user_id: int) -> Optional[User]:
        """Retrieve a user by primary key."""
        if hasattr(db, "query"):
            return db.query(User).filter(User.id == user_id).first()
        elif hasattr(db, "get"):
            return db.get(user_id)
        return None

    @classmethod
    def get_user_by_email(cls, db: Any, email: str) -> Optional[User]:
        """Retrieve a user by normalized email."""
        normalized_email = cls._normalize_email(email)

        if hasattr(db, "query"):
            return db.query(User).filter(User.email == normalized_email).first()
        elif hasattr(db, "find_by_email"):
            return db.find_by_email(normalized_email)
        return None

    @classmethod
    def get_user_by_username(cls, db: Any, username: str) -> Optional[User]:
        """Retrieve a user by normalized username."""
        normalized_username = cls._normalize_username(username)

        if hasattr(db, "query"):
            return db.query(User).filter(User.username == normalized_username).first()
        elif hasattr(db, "find_by_username"):
            return db.find_by_username(normalized_username)
        return None

    # --------------------------------------------------
    # CREATE USER
    # --------------------------------------------------

    @classmethod
    def create_user(cls, db: Any, user_create: UserCreate) -> User:
        """Create a user with normalized fields, duplicate checks, and password hashing."""

        normalized_email = cls._normalize_email(user_create.email)
        normalized_username = cls._normalize_username(user_create.username)

        # Check duplicate email
        existing_email = cls.get_user_by_email(db, normalized_email)
        if existing_email:
            raise DuplicateEmailError(
                f"User with email '{normalized_email}' is already registered."
            )

        # Check duplicate username
        existing_username = cls.get_user_by_username(db, normalized_username)
        if existing_username:
            raise DuplicateUsernameError(
                f"Username '{normalized_username}' is already taken."
            )

        # Hash password
        hashed_password = get_password_hash(user_create.password)

        # Create user
        db_user = User(
            email=normalized_email,
            username=normalized_username,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            is_active=(
                user_create.is_active
                if user_create.is_active is not None
                else True
            ),
        )

        # Save user
        if hasattr(db, "add") and hasattr(db, "commit"):
            try:
                db.add(db_user)
                db.commit()

                if hasattr(db, "refresh"):
                    db.refresh(db_user)

            except IntegrityError as exc:
                db.rollback()

                error_field = cls._get_integrity_error_field(exc)

                if error_field == "email":
                    raise DuplicateEmailError(
                        f"User with email '{normalized_email}' is already registered."
                    ) from exc

                if error_field == "username":
                    raise DuplicateUsernameError(
                        f"Username '{normalized_username}' is already taken."
                    ) from exc

                raise

        elif hasattr(db, "save"):
            db.save(db_user)

        return db_user

    # --------------------------------------------------
    # UPDATE USER
    # --------------------------------------------------

    @classmethod
    def update_user(
        cls,
        db: Any,
        user_id: int,
        user_update: UserUpdate,
    ) -> User:
        """Update user details with normalization and duplicate checks."""

        user = cls.get_user_by_id(db, user_id)

        if not user:
            raise UserNotFoundError(
                f"User with id {user_id} not found."
            )

        # Update email
        if user_update.email is not None:
            normalized_email = cls._normalize_email(user_update.email)
            current_email = cls._normalize_email(user.email)

            if normalized_email != current_email:
                existing_email = cls.get_user_by_email(db, normalized_email)

                if existing_email and existing_email.id != user_id:
                    raise DuplicateEmailError(
                        f"Email '{normalized_email}' is already registered "
                        "to another account."
                    )

            user.email = normalized_email

        # Update username
        if user_update.username is not None:
            normalized_username = cls._normalize_username(user_update.username)
            current_username = cls._normalize_username(user.username)

            if normalized_username != current_username:
                existing_username = cls.get_user_by_username(
                    db, normalized_username
                )

                if existing_username and existing_username.id != user_id:
                    raise DuplicateUsernameError(
                        f"Username '{normalized_username}' is already taken "
                        "by another user."
                    )

            user.username = normalized_username

        # Update password
        if user_update.password is not None:
            user.hashed_password = get_password_hash(user_update.password)

        # Update full name
        if user_update.full_name is not None:
            user.full_name = user_update.full_name

        # Update active status
        if user_update.is_active is not None:
            user.is_active = user_update.is_active

        # Update timestamp
        if hasattr(user, "updated_at"):
            user.updated_at = datetime.now(timezone.utc)

        # Commit changes
        if hasattr(db, "commit"):
            try:
                db.commit()

                if hasattr(db, "refresh"):
                    db.refresh(user)

            except IntegrityError as exc:
                db.rollback()

                error_field = cls._get_integrity_error_field(exc)

                if error_field == "email":
                    raise DuplicateEmailError(
                        "Email is already registered to another account."
                    ) from exc

                if error_field == "username":
                    raise DuplicateUsernameError(
                        "Username is already taken by another user."
                    ) from exc

                raise

        elif hasattr(db, "save"):
            db.save(user)

        return user

    # --------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------

    @classmethod
    def authenticate_user(
        cls,
        db: Any,
        username_or_email: str,
        password: str,
    ) -> Optional[User]:
        """Authenticate using email or username and verify password."""

        # Try email first
        user = cls.get_user_by_email(db, username_or_email)

        # Try username if email lookup fails
        if not user:
            user = cls.get_user_by_username(db, username_or_email)

        if not user:
            return None

        # Verify password
        if not verify_password(password, user.hashed_password):
            return None

        return user
