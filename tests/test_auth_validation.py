"""Tests for M2's validation and security helpers (no database needed).

Needs M2's code to be inside src/ (src/schemas/user.py and src/core/security.py).
Run:  python -m pytest tests/test_auth_validation.py -v
"""
from datetime import timedelta

import pytest

from src.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from src.schemas.user import (
    validate_email_format,
    validate_password_strength,
    validate_username_format,
)


def test_email_is_trimmed_and_lowercased():
    assert validate_email_format("  John@Example.COM ") == "john@example.com"


@pytest.mark.parametrize("bad", ["johnexample.com", "   ", "a@b@c.com", "a" * 250 + "@b.com"])
def test_bad_emails_rejected(bad):
    with pytest.raises(ValueError):
        validate_email_format(bad)


@pytest.mark.xfail(reason="email regex is loose: accepts a@b.., a@b.- and a@-b.com")
@pytest.mark.parametrize("bad", ["a@b..", "a@b.-", "a@-b.com"])
def test_gap_loose_email_regex(bad):
    with pytest.raises(ValueError):
        validate_email_format(bad)


def test_username_valid_and_trimmed():
    assert validate_username_format(" john_doe-1 ") == "john_doe-1"


@pytest.mark.parametrize("bad", ["ab", "a" * 51, "john doe", "john@doe"])
def test_bad_usernames_rejected(bad):
    with pytest.raises(ValueError):
        validate_username_format(bad)


def test_strong_password_accepted():
    assert validate_password_strength("SecurePass123!") == "SecurePass123!"


@pytest.mark.parametrize(
    "bad",
    ["Ab1!xyz", "securepass1!", "SECUREPASS1!", "SecurePass!!", "SecurePass123", "Aa1!" + "x" * 125],
)
def test_weak_passwords_rejected(bad):
    with pytest.raises(ValueError):
        validate_password_strength(bad)


def test_hash_and_verify():
    hashed = get_password_hash("SecurePass123!")
    assert hashed != "SecurePass123!"
    assert verify_password("SecurePass123!", hashed)
    assert not verify_password("WrongPass123!", hashed)
    assert not verify_password("", hashed)


def test_same_password_gives_different_hashes():
    assert get_password_hash("SecurePass123!") != get_password_hash("SecurePass123!")


def test_long_password_hash_still_verifies():
    pw = "Aa1!" + "x" * 120
    assert verify_password(pw, get_password_hash(pw))


def test_token_roundtrip():
    payload = decode_access_token(create_access_token({"sub": "1", "username": "john"}))
    assert payload["sub"] == "1"
    assert payload["username"] == "john"
    assert "exp" in payload and "iat" in payload


def test_expired_and_invalid_tokens_return_none():
    expired = create_access_token({"sub": "1"}, timedelta(seconds=-5))
    assert decode_access_token(expired) is None
    assert decode_access_token("not.a.token") is None
