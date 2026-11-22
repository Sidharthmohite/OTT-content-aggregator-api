
"""Unit tests for UserService business logic."""

from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.core.security import get_password_hash, verify_password
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.services.user_service import (
    DuplicateEmailError,
    DuplicateUsernameError,
    UserNotFoundError,
    UserService,
)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def make_user_data():
    return UserCreate(
        email="john@example.com",
        username="john_doe",
        password="SecurePass123!",
        full_name="John Doe",
    )


def make_user():
    return User(
        id=1,
        email="john@example.com",
        username="john_doe",
        hashed_password=get_password_hash("SecurePass123!"),
        full_name="John Doe",
        is_active=True,
    )


def make_mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    return db


# --------------------------------------------------
# UserService Tests
# --------------------------------------------------

class TestUserService:

    # --------------------------------------------------
    # Create User
    # --------------------------------------------------

    def test_create_user_successful(self):
        db = make_mock_db()
        payload = make_user_data()

        user = UserService.create_user(db, payload)

        assert user.email == "john@example.com"
        assert user.username == "john_doe"
        assert user.full_name == "John Doe"
        assert user.hashed_password != payload.password
        assert verify_password(payload.password, user.hashed_password)

        db.add.assert_called_once_with(user)
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(user)

    def test_duplicate_email_rejected(self, monkeypatch):
        db = make_mock_db()
        existing_user = make_user()

        monkeypatch.setattr(
            UserService,
            "get_user_by_email",
            staticmethod(lambda db, email: existing_user),
        )

        with pytest.raises(DuplicateEmailError):
            UserService.create_user(db, make_user_data())

        db.add.assert_not_called()
        db.commit.assert_not_called()

    def test_duplicate_email_case_insensitive_rejected(self, monkeypatch):
        db = make_mock_db()
        existing_user = make_user()

        monkeypatch.setattr(
            UserService,
            "get_user_by_email",
            staticmethod(lambda db, email: existing_user),
        )

        payload = UserCreate(
            email="JOHN@EXAMPLE.COM",
            username="another_user",
            password="SecurePass123!",
        )

        with pytest.raises(DuplicateEmailError):
            UserService.create_user(db, payload)

        db.add.assert_not_called()
        db.commit.assert_not_called()

    def test_duplicate_username_rejected(self, monkeypatch):
        db = make_mock_db()
        existing_user = make_user()

        monkeypatch.setattr(
            UserService,
            "get_user_by_email",
            staticmethod(lambda db, email: None),
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_username",
            staticmethod(lambda db, username: existing_user),
        )

        with pytest.raises(DuplicateUsernameError):
            UserService.create_user(db, make_user_data())

        db.add.assert_not_called()
        db.commit.assert_not_called()

    # --------------------------------------------------
    # Database Integrity Errors
    # --------------------------------------------------

    def test_create_user_username_integrity_error_rolls_back(self):
        db = make_mock_db()

        db.commit.side_effect = IntegrityError(
            "INSERT",
            {},
            Exception("UNIQUE constraint failed: users.username"),
        )

        with pytest.raises(DuplicateUsernameError):
            UserService.create_user(db, make_user_data())

        db.rollback.assert_called_once()

    def test_create_user_email_integrity_error_rolls_back(self):
        db = make_mock_db()

        db.commit.side_effect = IntegrityError(
            "INSERT",
            {},
            Exception("UNIQUE constraint failed: users.email"),
        )

        with pytest.raises(DuplicateEmailError):
            UserService.create_user(db, make_user_data())

        db.rollback.assert_called_once()
    def test_update_user_email_integrity_error_rolls_back(self, monkeypatch):
        db = make_mock_db()
        user = make_user()

        monkeypatch.setattr(
            UserService,
            "get_user_by_id",
            staticmethod(lambda db, user_id: user),
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_email",
            staticmethod(lambda db, email: None),
        )

        db.commit.side_effect = IntegrityError(
            "UPDATE",
            {},
            Exception("UNIQUE constraint failed: users.email"),
        )

        payload = UserUpdate(email="new@example.com")

        with pytest.raises(DuplicateEmailError):
            UserService.update_user(db, 1, payload)

        db.rollback.assert_called_once()


    def test_update_user_username_integrity_error_rolls_back(self, monkeypatch):
        db = make_mock_db()
        user = make_user()

        monkeypatch.setattr(
            UserService,
            "get_user_by_id",
            staticmethod(lambda db, user_id: user),
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_username",
            staticmethod(lambda db, username: None),
        )

        db.commit.side_effect = IntegrityError(
            "UPDATE",
            {},
            Exception("UNIQUE constraint failed: users.username"),
        )

        payload = UserUpdate(username="new_username")

        with pytest.raises(DuplicateUsernameError):
            UserService.update_user(db, 1, payload)

        db.rollback.assert_called_once()

    # --------------------------------------------------
    # Get User
    # --------------------------------------------------

    def test_get_user_by_id_and_email_and_username(self):
        user = make_user()

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user

        assert UserService.get_user_by_id(db, 1) == user
        assert UserService.get_user_by_email(
            db, " JOHN@EXAMPLE.COM "
        ) == user
        assert UserService.get_user_by_username(
            db, " john_doe "
        ) == user

    def test_get_user_by_id_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        result = UserService.get_user_by_id(db, 999)

        assert result is None

    # --------------------------------------------------
    # Update User
    # --------------------------------------------------

    def test_update_user_profile(self, monkeypatch):
        db = make_mock_db()
        user = make_user()

        monkeypatch.setattr(
            UserService,
            "get_user_by_id",
            staticmethod(lambda db, user_id: user),
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_email",
            staticmethod(lambda db, email: None),
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_username",
            staticmethod(lambda db, username: None),
        )

        payload = UserUpdate(full_name="Updated Name")

        result = UserService.update_user(db, 1, payload)

        assert result.full_name == "Updated Name"
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(user)

    def test_update_user_email(self, monkeypatch):
        db = make_mock_db()
        user = make_user()

        monkeypatch.setattr(
            UserService,
            "get_user_by_id",
            staticmethod(lambda db, user_id: user),
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_email",
            staticmethod(lambda db, email: None),
        )

        payload = UserUpdate(email="new@example.com")

        result = UserService.update_user(db, 1, payload)

        assert result.email == "new@example.com"
        db.commit.assert_called_once()

    def test_update_user_username(self, monkeypatch):
        db = make_mock_db()
        user = make_user()

        monkeypatch.setattr(
            UserService,
            "get_user_by_id",
            staticmethod(lambda db, user_id: user),
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_username",
            staticmethod(lambda db, username: None),
        )

        payload = UserUpdate(username="new_username")

        result = UserService.update_user(db, 1, payload)

        assert result.username == "new_username"
        db.commit.assert_called_once()

    def test_update_user_password_is_hashed(self, monkeypatch):
        db = make_mock_db()
        user = make_user()

        monkeypatch.setattr(
            UserService,
            "get_user_by_id",
            staticmethod(lambda db, user_id: user),
        )

        payload = UserUpdate(password="NewSecure123!")

        result = UserService.update_user(db, 1, payload)

        assert result.hashed_password != "NewSecure123!"
        assert verify_password("NewSecure123!", result.hashed_password)
        db.commit.assert_called_once()

    def test_update_user_email_duplicate_rejected(self, monkeypatch):
        db = make_mock_db()
        user = make_user()

        another_user = User(
            id=2,
            email="another@example.com",
            username="another_user",
            hashed_password="dummy",
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_id",
            staticmethod(lambda db, user_id: user),
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_email",
            staticmethod(lambda db, email: another_user),
        )

        payload = UserUpdate(email="another@example.com")

        with pytest.raises(DuplicateEmailError):
            UserService.update_user(db, 1, payload)

        db.commit.assert_not_called()

    def test_update_user_username_duplicate_rejected(self, monkeypatch):
        db = make_mock_db()
        user = make_user()

        another_user = User(
            id=2,
            email="another@example.com",
            username="another_user",
            hashed_password="dummy",
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_id",
            staticmethod(lambda db, user_id: user),
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_username",
            staticmethod(lambda db, username: another_user),
        )

        payload = UserUpdate(username="another_user")

        with pytest.raises(DuplicateUsernameError):
            UserService.update_user(db, 1, payload)

        db.commit.assert_not_called()
    
    def test_update_own_email_normalizes_without_duplicate(self, monkeypatch):
        db = make_mock_db()
        user = make_user()

        original_email = user.email

        monkeypatch.setattr(
            UserService,
            "get_user_by_id",
            staticmethod(lambda db, user_id: user),
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_email",
            staticmethod(lambda db, email: None),
        )

        payload = UserUpdate(email=f" {original_email.upper()} ")

        result = UserService.update_user(db, 1, payload)

        assert result.email == original_email.strip().lower()
        db.commit.assert_called_once()

    def test_update_own_username_normalizes_without_duplicate(selfself, monkeypatch):
        db = make_mock_db()
        user = make_user()

        original_username = user.username

        monkeypatch.setattr(
            UserService,
            "get_user_by_id",
            staticmethod(lambda db, user_id: user),
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_username",
            staticmethod(lambda db, username: None),
        )

        payload = UserUpdate(username=f" {original_username} ")

        result = UserService.update_user(db, 1, payload)

        assert result.username == original_username.strip()
        db.commit.assert_called_once()


    def test_update_nonexistent_user(self, monkeypatch):
        db = make_mock_db()

        monkeypatch.setattr(
            UserService,
            "get_user_by_id",
            staticmethod(lambda db, user_id: None),
        )

        with pytest.raises(UserNotFoundError):
            UserService.update_user(db, 999, UserUpdate(full_name="Unknown"))

        db.commit.assert_not_called()

    # --------------------------------------------------
    # Authentication
    # --------------------------------------------------

    def test_authenticate_user_success(self, monkeypatch):
        user = make_user()

        monkeypatch.setattr(
            UserService,
            "get_user_by_email",
            staticmethod(lambda db, value: None),
        )

        monkeypatch.setattr(
            UserService,
            "get_user_by_username",
            staticmethod(lambda db, value: user),
        )

        result = UserService.authenticate_user(
            MagicMock(),
            "john_doe",
            "SecurePass123!",
        )

        assert result == user

    def test_authenticate_user_invalid_credentials(self, monkeypatch):
        user = make_user()

        monkeypatch.setattr(
            UserService,
            "get_user_by_email",
            staticmethod(lambda db, value: user),
        )

        result = UserService.authenticate_user(
            MagicMock(),
            "john@example.com",
            "WrongPassword123!",
        )

        assert result is None

    # --------------------------------------------------
    # Normalization
    # --------------------------------------------------

    def test_create_user_normalizes_email_and_username(self):
        db = make_mock_db()

        payload = UserCreate.model_construct(
            email=" JOHN@EXAMPLE.COM ",
            username=" john_doe ",
            password="SecurePass123!",
            full_name="John Doe",
            is_active=True,
        )

        user = UserService.create_user(db, payload)

        assert user.email == "john@example.com"
        assert user.username == "john_doe"
