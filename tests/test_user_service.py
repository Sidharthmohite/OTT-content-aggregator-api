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
# Normalization helpers
# --------------------------------------------------

def test_normalize_email():
    assert UserService._normalize_email(" JOHN@EXAMPLE.COM ") == "john@example.com"


def test_normalize_username():
    assert UserService._normalize_username(" john_doe ") == "john_doe"


def test_integrity_error_field_email():
    exc = IntegrityError("INSERT", {}, Exception("duplicate email"))
    assert UserService._get_integrity_error_field(exc) == "email"


def test_integrity_error_field_username():
    exc = IntegrityError("INSERT", {}, Exception("duplicate username"))
    assert UserService._get_integrity_error_field(exc) == "username"


def test_integrity_error_field_constraint_email():
    original = Exception("duplicate")
    original.diag = MagicMock(constraint_name="users_email_key")
    exc = IntegrityError("INSERT", {}, original)

    assert UserService._get_integrity_error_field(exc) == "email"


def test_integrity_error_field_constraint_username():
    original = Exception("duplicate")
    original.diag = MagicMock(constraint_name="users_username_key")
    exc = IntegrityError("INSERT", {}, original)

    assert UserService._get_integrity_error_field(exc) == "username"


def test_integrity_error_field_unknown():
    exc = IntegrityError("INSERT", {}, Exception("duplicate value"))
    assert UserService._get_integrity_error_field(exc) is None


# --------------------------------------------------
# User retrieval
# --------------------------------------------------

def test_get_user_by_id_using_get_fallback():
    db = MagicMock()
    del db.query

    expected = make_user()
    db.get.return_value = expected

    assert UserService.get_user_by_id(db, 1) == expected


def test_get_user_by_id_no_supported_method():
    db = object()

    assert UserService.get_user_by_id(db, 1) is None


def test_get_user_by_email_using_fallback():
    db = MagicMock()
    del db.query

    db.find_by_email.return_value = None

    assert UserService.get_user_by_email(db, " JOHN@EXAMPLE.COM ") is None
    db.find_by_email.assert_called_once_with("john@example.com")


def test_get_user_by_email_no_supported_method():
    assert UserService.get_user_by_email(object(), " JOHN@EXAMPLE.COM ") is None


def test_get_user_by_username_using_fallback():
    db = MagicMock()
    del db.query

    db.find_by_username.return_value = None

    assert UserService.get_user_by_username(db, " john_doe ") is None
    db.find_by_username.assert_called_once_with("john_doe")


def test_get_user_by_username_no_supported_method():
    assert UserService.get_user_by_username(object(), " john_doe ") is None


# --------------------------------------------------
# Create user
# --------------------------------------------------

def test_create_user_successful():
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


def test_create_user_duplicate_email(monkeypatch):
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


def test_create_user_duplicate_username(monkeypatch):
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


def test_create_user_normalizes_email_and_username():
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


def test_create_user_inactive():
    db = make_mock_db()

    payload = UserCreate.model_construct(
        email="john@example.com",
        username="john_doe",
        password="SecurePass123!",
        full_name="John Doe",
        is_active=False,
    )

    user = UserService.create_user(db, payload)

    assert user.is_active is False


def test_create_user_save_fallback(monkeypatch):
    db = MagicMock()
    del db.add
    del db.commit

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

    user = UserService.create_user(db, make_user_data())

    db.save.assert_called_once_with(user)


def test_create_user_unknown_integrity_error():
    db = make_mock_db()

    db.commit.side_effect = IntegrityError(
        "INSERT", {}, Exception("unknown integrity issue")
    )

    with pytest.raises(IntegrityError):
        UserService.create_user(db, make_user_data())

    db.rollback.assert_called_once()


def test_create_user_email_integrity_error():
    db = make_mock_db()

    db.commit.side_effect = IntegrityError(
        "INSERT", {}, Exception("unique users.email")
    )

    with pytest.raises(DuplicateEmailError):
        UserService.create_user(db, make_user_data())

    db.rollback.assert_called_once()


def test_create_user_username_integrity_error():
    db = make_mock_db()

    db.commit.side_effect = IntegrityError(
        "INSERT", {}, Exception("unique users.username")
    )

    with pytest.raises(DuplicateUsernameError):
        UserService.create_user(db, make_user_data())

    db.rollback.assert_called_once()


def test_create_user_refresh_optional(monkeypatch):
    db = make_mock_db()
    del db.refresh

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

    user = UserService.create_user(db, make_user_data())

    assert user.email == "john@example.com"


# --------------------------------------------------
# Update user
# --------------------------------------------------

def test_update_user_success(monkeypatch):
    db = make_mock_db()
    user = make_user()

    monkeypatch.setattr(
        UserService,
        "get_user_by_id",
        staticmethod(lambda db, user_id: user),
    )

    result = UserService.update_user(db, 1, UserUpdate(full_name="Updated Name"))

    assert result.full_name == "Updated Name"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user)


def test_update_user_email(monkeypatch):
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

    result = UserService.update_user(db, 1, UserUpdate(email="new@example.com"))

    assert result.email == "new@example.com"


def test_update_user_username(monkeypatch):
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

    result = UserService.update_user(db, 1, UserUpdate(username="new_username"))

    assert result.username == "new_username"


def test_update_user_password(monkeypatch):
    db = make_mock_db()
    user = make_user()

    monkeypatch.setattr(
        UserService,
        "get_user_by_id",
        staticmethod(lambda db, user_id: user),
    )

    result = UserService.update_user(db, 1, UserUpdate(password="NewSecure123!"))

    assert verify_password("NewSecure123!", result.hashed_password)


def test_update_user_is_active(monkeypatch):
    db = make_mock_db()
    user = make_user()

    monkeypatch.setattr(
        UserService,
        "get_user_by_id",
        staticmethod(lambda db, user_id: user),
    )

    result = UserService.update_user(db, 1, UserUpdate(is_active=False))

    assert result.is_active is False


def test_update_user_duplicate_email(monkeypatch):
    db = make_mock_db()
    user = make_user()
    another_user = make_user()
    another_user.id = 2

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

    with pytest.raises(DuplicateEmailError):
        UserService.update_user(db, 1, UserUpdate(email="another@example.com"))

    db.commit.assert_not_called()


def test_update_user_duplicate_username(monkeypatch):
    db = make_mock_db()
    user = make_user()
    another_user = make_user()
    another_user.id = 2

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

    with pytest.raises(DuplicateUsernameError):
        UserService.update_user(db, 1, UserUpdate(username="another_user"))

    db.commit.assert_not_called()


def test_update_same_email(monkeypatch):
    db = make_mock_db()
    user = make_user()

    monkeypatch.setattr(
        UserService,
        "get_user_by_id",
        staticmethod(lambda db, user_id: user),
    )

    result = UserService.update_user(
        db, 1, UserUpdate(email=" JOHN@EXAMPLE.COM ")
    )

    assert result.email == "john@example.com"


def test_update_same_username(monkeypatch):
    db = make_mock_db()
    user = make_user()

    monkeypatch.setattr(
        UserService,
        "get_user_by_id",
        staticmethod(lambda db, user_id: user),
    )

    result = UserService.update_user(
        db, 1, UserUpdate(username=" john_doe ")
    )

    assert result.username == "john_doe"


def test_update_user_not_found(monkeypatch):
    db = make_mock_db()

    monkeypatch.setattr(
        UserService,
        "get_user_by_id",
        staticmethod(lambda db, user_id: None),
    )

    with pytest.raises(UserNotFoundError):
        UserService.update_user(db, 999, UserUpdate(full_name="Unknown"))

    db.commit.assert_not_called()


def test_update_user_save_fallback(monkeypatch):
    db = MagicMock()
    del db.commit

    user = make_user()

    monkeypatch.setattr(
        UserService,
        "get_user_by_id",
        staticmethod(lambda db, user_id: user),
    )

    UserService.update_user(db, 1, UserUpdate(full_name="Updated"))

    db.save.assert_called_once_with(user)


def test_update_user_unknown_integrity_error(monkeypatch):
    db = make_mock_db()
    user = make_user()

    monkeypatch.setattr(
        UserService,
        "get_user_by_id",
        staticmethod(lambda db, user_id: user),
    )

    db.commit.side_effect = IntegrityError(
        "UPDATE", {}, Exception("unknown error")
    )

    with pytest.raises(IntegrityError):
        UserService.update_user(db, 1, UserUpdate(full_name="Updated"))

    db.rollback.assert_called_once()


def test_update_user_email_integrity_error(monkeypatch):
    db = make_mock_db()
    user = make_user()

    monkeypatch.setattr(
        UserService,
        "get_user_by_id",
        staticmethod(lambda db, user_id: user),
    )

    db.commit.side_effect = IntegrityError(
        "UPDATE", {}, Exception("unique email")
    )

    with pytest.raises(DuplicateEmailError):
        UserService.update_user(db, 1, UserUpdate(email="new@example.com"))

    db.rollback.assert_called_once()


def test_update_user_username_integrity_error(monkeypatch):
    db = make_mock_db()
    user = make_user()

    monkeypatch.setattr(
        UserService,
        "get_user_by_id",
        staticmethod(lambda db, user_id: user),
    )

    db.commit.side_effect = IntegrityError(
        "UPDATE", {}, Exception("unique username")
    )

    with pytest.raises(DuplicateUsernameError):
        UserService.update_user(db, 1, UserUpdate(username="new_username"))

    db.rollback.assert_called_once()


def test_update_user_refresh_optional(monkeypatch):
    db = make_mock_db()
    del db.refresh

    user = make_user()

    monkeypatch.setattr(
        UserService,
        "get_user_by_id",
        staticmethod(lambda db, user_id: user),
    )

    result = UserService.update_user(db, 1, UserUpdate(full_name="Updated"))

    assert result.full_name == "Updated"


# --------------------------------------------------
# Authentication
# --------------------------------------------------

def test_authenticate_user_by_email(monkeypatch):
    user = make_user()

    monkeypatch.setattr(
        UserService,
        "get_user_by_email",
        staticmethod(lambda db, value: user),
    )

    result = UserService.authenticate_user(
        MagicMock(), "john@example.com", "SecurePass123!"
    )

    assert result == user


def test_authenticate_user_by_username(monkeypatch):
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
        MagicMock(), "john_doe", "SecurePass123!"
    )

    assert result == user


def test_authenticate_user_not_found(monkeypatch):
    monkeypatch.setattr(
        UserService,
        "get_user_by_email",
        staticmethod(lambda db, value: None),
    )

    monkeypatch.setattr(
        UserService,
        "get_user_by_username",
        staticmethod(lambda db, value: None),
    )

    assert UserService.authenticate_user(MagicMock(), "unknown", "password") is None


def test_authenticate_user_wrong_password(monkeypatch):
    user = make_user()

    monkeypatch.setattr(
        UserService,
        "get_user_by_email",
        staticmethod(lambda db, value: user),
    )

    assert UserService.authenticate_user(
        MagicMock(), "john@example.com", "WrongPassword!"
    ) is None
