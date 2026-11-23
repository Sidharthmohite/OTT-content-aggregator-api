"""Tests for Pydantic user schemas."""

import pytest

from src.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    validate_email_format,
    validate_username_format,
    validate_password_strength,
)


def test_userbase_valid_data():
    user = UserBase(
        email="  JOHN@example.com ",
        username=" john_doe ",
        full_name=" John Doe ",
    )

    assert user.email == "john@example.com"
    assert user.username == "john_doe"
    assert user.full_name == "John Doe"


def test_userbase_empty_full_name_becomes_none():
    user = UserBase(
        email="john@example.com",
        username="john_doe",
        full_name="   ",
    )

    assert user.full_name is None


def test_userbase_optional_full_name_none():
    user = UserBase(
        email="john@example.com",
        username="john_doe",
        full_name=None,
    )

    assert user.full_name is None


def test_usercreate_valid_data():
    user = UserCreate(
        email="john@example.com",
        username="john_doe",
        full_name="John Doe",
        password="SecurePass123!",
    )

    assert user.email == "john@example.com"
    assert user.username == "john_doe"
    assert user.password == "SecurePass123!"


def test_userupdate_all_fields():
    user = UserUpdate(
        email="  NEW@example.com ",
        username=" new_user ",
        full_name=" New Name ",
        password="NewPass123!",
        is_active=False,
    )

    assert user.email == "new@example.com"
    assert user.username == "new_user"
    assert user.full_name == "New Name"
    assert user.password == "NewPass123!"
    assert user.is_active is False


def test_userupdate_optional_fields_none():
    user = UserUpdate(
        email=None,
        username=None,
        full_name=None,
        password=None,
        is_active=None,
    )

    assert user.email is None
    assert user.username is None
    assert user.full_name is None
    assert user.password is None
    assert user.is_active is None


def test_userupdate_empty_full_name_becomes_none():
    user = UserUpdate(full_name="   ")

    assert user.full_name is None


@pytest.mark.parametrize(
    "data",
    [
        {"email": "invalid-email"},
        {"username": "ab"},
        {"password": "weak"},
    ],
)
def test_userupdate_invalid_values_rejected(data):
    with pytest.raises(ValueError):
        UserUpdate(**data)


def test_email_exceeding_maximum_length_rejected():
    email = "a" * 250 + "@example.com"

    with pytest.raises(ValueError, match="255 characters"):
        validate_email_format(email)


def test_username_exceeding_maximum_length_rejected():
    username = "a" * 51

    with pytest.raises(ValueError, match="50 characters"):
        validate_username_format(username)


def test_password_exceeding_maximum_length_rejected():
    password = "Aa1!" + "x" * 125

    with pytest.raises(ValueError, match="128 characters"):
        validate_password_strength(password)

def test_email_non_string_rejected():
    with pytest.raises(ValueError, match="Email must be a valid string"):
        validate_email_format(123)


def test_username_non_string_rejected():
    with pytest.raises(ValueError, match="Username must be a valid string"):
        validate_username_format(123)


def test_password_non_string_rejected():
    with pytest.raises(ValueError, match="Password must be a valid string"):
        validate_password_strength(123)
