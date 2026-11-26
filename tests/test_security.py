import hashlib
from datetime import timedelta

import pytest
import jwt

from src.core import security


def test_verify_password_empty_password():
    assert security.verify_password("", "some_hash") is False


def test_verify_password_empty_hash():
    assert security.verify_password("password", "") is False


def test_verify_password_pbkdf2_correct():
    password = "test123"
    salt = "testsalt"

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()

    stored_hash = f"pbkdf2_sha256${salt}${hashed}"

    assert security.verify_password(password, stored_hash) is True


def test_verify_password_pbkdf2_wrong():
    password = "test123"
    salt = "testsalt"

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()

    stored_hash = f"pbkdf2_sha256${salt}${hashed}"

    assert security.verify_password("wrongpassword", stored_hash) is False


def test_verify_password_invalid_pbkdf2_format():
    assert security.verify_password("password", "pbkdf2_sha256$invalid") is False


def test_get_password_hash_empty():
    with pytest.raises(ValueError, match="Password cannot be empty"):
        security.get_password_hash("")


def test_get_password_hash_and_verify():
    password = "MyTestPassword123"
    hashed = security.get_password_hash(password)

    assert hashed != password
    assert security.verify_password(password, hashed) is True
    assert security.verify_password("wrongpassword", hashed) is False


def test_create_access_token_and_decode():
    token = security.create_access_token({"sub": "1"})
    payload = security.decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "1"


def test_create_access_token_custom_expiry():
    token = security.create_access_token(
        {"sub": "2"},
        expires_delta=timedelta(minutes=5),
    )

    payload = security.decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "2"


def test_decode_invalid_token():
    assert security.decode_access_token("invalid.token.value") is None


def test_get_current_user_id_valid():
    token = security.create_access_token({"sub": "123"})
    user_id = security.get_current_user_id(token)

    assert user_id == 123


def test_get_current_user_id_missing_sub():
    token = security.create_access_token({"username": "test"})
    with pytest.raises(Exception) as exc:
        security.get_current_user_id(token)

    assert exc.value.status_code == 401


def test_get_current_user_id_invalid_sub():
    token = security.create_access_token({"sub": "abc"})
    with pytest.raises(Exception) as exc:
        security.get_current_user_id(token)

    assert exc.value.status_code == 401
def test_verify_password_pbkdf2_malformed_parts():
    assert security.verify_password(
        "password",
        "pbkdf2_sha256$salt$hash$extra",
    ) is False


def test_verify_password_pbkdf2_exception():
    # Simulates an invalid password input causing an exception
    assert security.verify_password("password", "pbkdf2_sha256$") is False


def test_passlib_verify_exception_returns_false(monkeypatch):
    monkeypatch.setattr(security, "HAS_PASSLIB", True)

    class BrokenPasswordContext:
        def verify(self, plain, hashed):
            raise RuntimeError("verification failure")

    monkeypatch.setattr(security, "pwd_context", BrokenPasswordContext())

    assert security.verify_password("password", "invalid_hash") is False


def test_password_hash_falls_back_when_passlib_fails(monkeypatch):
    monkeypatch.setattr(security, "HAS_PASSLIB", True)

    class BrokenPasswordContext:
        def hash(self, password):
            raise RuntimeError("hash failure")

    monkeypatch.setattr(security, "pwd_context", BrokenPasswordContext())

    hashed = security.get_password_hash("SecurePass123!")

    assert hashed.startswith("pbkdf2_sha256$")
    assert security.verify_password("SecurePass123!", hashed) is True
def test_pbkdf2_verification_exception(monkeypatch):
    def broken_pbkdf2(*args, **kwargs):
        raise RuntimeError("PBKDF2 failure")

    monkeypatch.setattr(
        security.hashlib,
        "pbkdf2_hmac",
        broken_pbkdf2,
    )

    assert security.verify_password(
        "password",
        "pbkdf2_sha256$salt$hash",
    ) is False


def test_verify_password_passlib_disabled(monkeypatch):
    monkeypatch.setattr(security, "HAS_PASSLIB", False)
    monkeypatch.setattr(security, "pwd_context", None)

    assert security.verify_password("password", "unknown_hash") is False


def test_current_user_id_invalid_token():
    with pytest.raises(Exception) as exc:
        security.get_current_user_id("invalid.token.value")

    assert exc.value.status_code == 401
