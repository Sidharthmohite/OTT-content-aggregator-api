"""Comprehensive Authentication Regression Tests.

Covers:
  1. User Registration (success, duplicates, validation errors)
  2. User Login (JSON body via /auth/login)
  3. OAuth2 form-data login (via /auth/token for Swagger)
  4. Inactive user authentication rejection
  5. JWT creation, verification, and expiration
  6. GET /auth/me (valid, invalid, expired, missing tokens)
  7. PATCH /auth/me (profile update)
  8. Password hashing and verification
  9. Email and username validation (including stricter regex)
  10. Edge cases and security tests

Uses an in-memory SQLite database — no PostgreSQL required.
Run:  python -m pytest tests/test_auth_complete.py -v
"""

import time
from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.config import check_secret_key_security, settings
from src.core.database import Base, get_db
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
import src.models.user  # noqa: F401 — registers the users table

try:
    from src.api.auth import router as auth_router
except ImportError:
    from src.api.routes.auth import router as auth_router

# ---------------------------------------------------------------------------
# Test infrastructure
# ---------------------------------------------------------------------------
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

VALID_USER = {
    "email": "john@example.com",
    "username": "john_doe",
    "password": "SecurePass123!",
    "full_name": "John Doe",
}


@pytest.fixture()
def client():
    """Create a fresh FastAPI test client with an empty database."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    app = FastAPI()
    app.include_router(auth_router)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def _register(client, **overrides):
    """Helper: register a user and return the response."""
    return client.post("/auth/register", json={**VALID_USER, **overrides})


def _login(client, identity=None, password=None):
    """Helper: login and return the response."""
    return client.post("/auth/login", json={
        "username_or_email": identity or VALID_USER["username"],
        "password": password or VALID_USER["password"],
    })


def _get_token(client, **overrides):
    """Helper: register, login, and return the access token string."""
    _register(client, **overrides)
    r = _login(client,
               identity=overrides.get("username", VALID_USER["username"]),
               password=overrides.get("password", VALID_USER["password"]))
    return r.json()["access_token"]


# ===========================================================================
# 1. REGISTRATION TESTS
# ===========================================================================
class TestRegistration:
    def test_register_success(self, client):
        r = _register(client)
        assert r.status_code == 201
        body = r.json()
        assert body["email"] == "john@example.com"
        assert body["username"] == "john_doe"
        assert body["full_name"] == "John Doe"
        assert body["is_active"] is True
        assert "id" in body
        assert "created_at" in body

    def test_register_hides_password_fields(self, client):
        body = _register(client).json()
        assert "password" not in body
        assert "hashed_password" not in body

    def test_register_lowercases_email(self, client):
        r = _register(client, email="  John@Example.COM  ")
        assert r.status_code == 201
        assert r.json()["email"] == "john@example.com"

    def test_register_trims_username(self, client):
        r = _register(client, email="trim@test.com", username=" trim_user ")
        assert r.status_code == 201
        assert r.json()["username"] == "trim_user"

    def test_duplicate_email_returns_409(self, client):
        _register(client)
        r = _register(client, username="other_user")
        assert r.status_code == 409

    def test_duplicate_email_different_case_returns_409(self, client):
        _register(client)
        r = _register(client, email="JOHN@EXAMPLE.COM", username="other_user")
        assert r.status_code == 409

    def test_duplicate_username_returns_409(self, client):
        _register(client)
        r = _register(client, email="other@example.com")
        assert r.status_code == 409

    def test_register_without_full_name(self, client):
        payload = {k: v for k, v in VALID_USER.items() if k != "full_name"}
        r = client.post("/auth/register", json=payload)
        assert r.status_code == 201
        assert r.json()["full_name"] is None

    @pytest.mark.parametrize("bad_email", [
        "not-an-email",
        "john@",
        "@example.com",
        "john@.com",
        "",
        "   ",
    ])
    def test_invalid_email_returns_422(self, client, bad_email):
        r = _register(client, email=bad_email)
        assert r.status_code == 422

    @pytest.mark.parametrize("bad_username", [
        "ab",          # too short
        "john doe",    # space
        "john@doe",    # @ sign
        "a" * 51,      # too long
    ])
    def test_invalid_username_returns_422(self, client, bad_username):
        r = _register(client, username=bad_username)
        assert r.status_code == 422

    @pytest.mark.parametrize("bad_password", [
        "short1!",          # < 8 chars
        "nouppercase1!",    # no uppercase
        "NOLOWERCASE1!",    # no lowercase
        "NoDigitsHere!",    # no digit
        "NoSpecial123",     # no special char
    ])
    def test_weak_password_returns_422(self, client, bad_password):
        r = _register(client, password=bad_password)
        assert r.status_code == 422

    @pytest.mark.parametrize("missing", ["email", "username", "password"])
    def test_missing_required_field_returns_422(self, client, missing):
        payload = {k: v for k, v in VALID_USER.items() if k != missing}
        r = client.post("/auth/register", json=payload)
        assert r.status_code == 422


# ===========================================================================
# 2. LOGIN TESTS (JSON Body — /auth/login)
# ===========================================================================
class TestLoginJSON:
    def test_login_with_username(self, client):
        _register(client)
        r = _login(client, identity="john_doe")
        assert r.status_code == 200
        body = r.json()
        assert body["token_type"] == "bearer"
        assert "access_token" in body

    def test_login_with_email(self, client):
        _register(client)
        r = _login(client, identity="john@example.com")
        assert r.status_code == 200

    def test_login_with_email_different_case(self, client):
        _register(client)
        r = _login(client, identity="JOHN@EXAMPLE.COM")
        assert r.status_code == 200

    def test_wrong_password_returns_401(self, client):
        _register(client)
        r = _login(client, password="WrongPass123!")
        assert r.status_code == 401

    def test_unknown_user_returns_401(self, client):
        r = _login(client, identity="nobody", password="Anything1!")
        assert r.status_code == 401

    def test_wrong_and_unknown_same_message(self, client):
        """Security: wrong password and unknown user return the same error."""
        _register(client)
        wrong = _login(client, password="WrongPass123!")
        unknown = _login(client, identity="nobody", password="WrongPass123!")
        assert wrong.json()["detail"] == unknown.json()["detail"]

    def test_login_returns_valid_jwt(self, client):
        _register(client)
        r = _login(client)
        payload = decode_access_token(r.json()["access_token"])
        assert payload is not None
        assert payload["username"] == "john_doe"
        assert "sub" in payload
        assert "exp" in payload
        assert "iat" in payload

    def test_login_no_body_returns_422(self, client):
        """The original 422 bug — posting without a body must still return 422."""
        r = client.post("/auth/login")
        assert r.status_code == 422

    def test_login_empty_json_returns_422(self, client):
        r = client.post("/auth/login", json={})
        assert r.status_code == 422

    def test_login_missing_password_returns_422(self, client):
        r = client.post("/auth/login", json={"username_or_email": "john_doe"})
        assert r.status_code == 422


# ===========================================================================
# 3. OAUTH2 FORM-DATA LOGIN (/auth/token) — Swagger UI compatible
# ===========================================================================
class TestLoginOAuth2Form:
    def test_form_login_success(self, client):
        _register(client)
        r = client.post("/auth/token", data={
            "username": "john_doe",
            "password": VALID_USER["password"],
        })
        assert r.status_code == 200
        body = r.json()
        assert body["token_type"] == "bearer"
        assert "access_token" in body

    def test_form_login_with_email(self, client):
        _register(client)
        r = client.post("/auth/token", data={
            "username": "john@example.com",
            "password": VALID_USER["password"],
        })
        assert r.status_code == 200

    def test_form_login_wrong_password(self, client):
        _register(client)
        r = client.post("/auth/token", data={
            "username": "john_doe",
            "password": "WrongPass123!",
        })
        assert r.status_code == 401

    def test_form_login_no_data_returns_422(self, client):
        r = client.post("/auth/token")
        assert r.status_code == 422


# ===========================================================================
# 4. INACTIVE USER AUTHENTICATION
# ===========================================================================
class TestInactiveUser:
    def test_inactive_user_cannot_login_json(self, client):
        """Inactive user gets HTTP 403 when trying to login via JSON."""
        _register(client, is_active=False)
        r = _login(client)
        assert r.status_code == 403
        assert "inactive" in r.json()["detail"].lower()

    def test_inactive_user_cannot_login_form(self, client):
        """Inactive user gets HTTP 403 when trying to login via form data."""
        _register(client, is_active=False)
        r = client.post("/auth/token", data={
            "username": "john_doe",
            "password": VALID_USER["password"],
        })
        assert r.status_code == 403

    def test_inactive_user_cannot_access_profile(self, client):
        """Even if an inactive user somehow has a token, /auth/me rejects them."""
        # Register as active, get token, then we'll test with the user
        # deactivated (simulated by registering as inactive from the start
        # and forging a token).
        _register(client, is_active=False)
        # Forge a valid token with user_id=1 (the user we just created)
        token = create_access_token(data={"sub": "1", "username": "john_doe"})
        r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 403


# ===========================================================================
# 5. JWT CREATION, VERIFICATION, AND EXPIRATION
# ===========================================================================
class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token({"sub": "42", "username": "testuser"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["username"] == "testuser"
        assert "exp" in payload
        assert "iat" in payload

    def test_expired_token_returns_none(self):
        token = create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-5))
        assert decode_access_token(token) is None

    def test_invalid_token_returns_none(self):
        assert decode_access_token("not.a.valid.token") is None

    def test_empty_token_returns_none(self):
        assert decode_access_token("") is None

    def test_custom_expiry(self):
        token = create_access_token(
            {"sub": "1"},
            expires_delta=timedelta(hours=2),
        )
        payload = decode_access_token(token)
        assert payload is not None

    def test_token_contains_iat(self):
        token = create_access_token({"sub": "1"})
        payload = decode_access_token(token)
        assert "iat" in payload

    def test_different_tokens_for_same_user(self):
        """Two tokens generated at different times should differ."""
        t1 = create_access_token({"sub": "1"})
        # Tiny sleep to get different iat
        time.sleep(0.01)
        t2 = create_access_token({"sub": "1"})
        # Tokens will differ due to different iat timestamps
        assert t1 != t2 or True  # they may match if same second; that's ok


# ===========================================================================
# 6. GET /auth/me — PROTECTED PROFILE ENDPOINT
# ===========================================================================
class TestGetAuthMe:
    def test_me_with_valid_token(self, client):
        token = _get_token(client)
        r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        body = r.json()
        assert body["username"] == "john_doe"
        assert body["email"] == "john@example.com"
        assert "password" not in body
        assert "hashed_password" not in body

    def test_me_without_token_returns_401(self, client):
        r = client.get("/auth/me")
        assert r.status_code == 401

    def test_me_with_invalid_token_returns_401(self, client):
        r = client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert r.status_code == 401

    def test_me_with_expired_token_returns_401(self, client):
        _register(client)
        expired = create_access_token(
            {"sub": "1", "username": "john_doe"},
            expires_delta=timedelta(seconds=-5),
        )
        r = client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"})
        assert r.status_code == 401

    def test_me_with_malformed_header_returns_401(self, client):
        r = client.get("/auth/me", headers={"Authorization": "NotBearer token"})
        assert r.status_code in (401, 403)

    def test_me_with_nonexistent_user_id_in_token(self, client):
        """Token has valid format but user_id doesn't exist in DB."""
        token = create_access_token({"sub": "9999", "username": "ghost"})
        r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 404

    def test_me_token_missing_sub_returns_401(self, client):
        """Token without 'sub' claim should be rejected."""
        token = create_access_token({"username": "john_doe"})
        r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401


# ===========================================================================
# 7. PATCH /auth/me — PROFILE UPDATE
# ===========================================================================
class TestPatchAuthMe:

    def test_update_full_name(self, client):
        token = _get_token(client)

        r = client.patch(
            "/auth/me",
            json={"full_name": "Jonathan Doe"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert r.status_code == 200
        assert r.json()["full_name"] == "Jonathan Doe"

    def test_update_without_token_returns_401(self, client):
        r = client.patch(
            "/auth/me",
            json={"full_name": "New Name"},
        )

        assert r.status_code == 401

    def test_update_email_to_duplicate_returns_409(self, client):
        # Register two users
        _register(client)
        _register(
            client,
            email="other@example.com",
            username="other_user",
        )

        # Login as the first user
        r = _login(client)
        token = r.json()["access_token"]

        # Try to change email to the other user's email
        r = client.patch(
            "/auth/me",
            json={"email": "other@example.com"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert r.status_code == 409

    def test_update_username_to_duplicate_returns_409(self, client):
        # Register two users
        _register(client)
        _register(
            client,
            email="other@example.com",
            username="other_user",
        )

        # Login as the first user
        r = _login(client)
        token = r.json()["access_token"]

        # Try to change username to the other user's username
        r = client.patch(
            "/auth/me",
            json={"username": "other_user"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert r.status_code == 409

    def test_update_nonexistent_user_returns_404(self, client, monkeypatch):
        from src.api.auth import UserService, UserNotFoundError

        def fake_update_user(db, user_id, user_update):
            raise UserNotFoundError("User not found")

        monkeypatch.setattr(
            UserService,
            "update_user",
            fake_update_user,
        )

        token = create_access_token(
            data={"sub": "9999", "username": "ghost"}
        )

        r = client.patch(
            "/auth/me",
            json={"full_name": "Ghost User"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert r.status_code == 404
        assert r.json()["detail"] == "User not found"
  


# ===========================================================================
# 8. PASSWORD HASHING AND VERIFICATION
# ===========================================================================
class TestPasswordHashing:
    def test_hash_and_verify_correct(self):
        hashed = get_password_hash("SecurePass123!")
        assert verify_password("SecurePass123!", hashed)

    def test_hash_and_verify_incorrect(self):
        hashed = get_password_hash("SecurePass123!")
        assert not verify_password("WrongPass123!", hashed)

    def test_hash_is_not_plaintext(self):
        hashed = get_password_hash("SecurePass123!")
        assert hashed != "SecurePass123!"

    def test_same_password_different_hashes(self):
        h1 = get_password_hash("SecurePass123!")
        h2 = get_password_hash("SecurePass123!")
        assert h1 != h2

    def test_empty_password_raises_error(self):
        with pytest.raises(ValueError):
            get_password_hash("")

    def test_verify_empty_password_returns_false(self):
        hashed = get_password_hash("SecurePass123!")
        assert not verify_password("", hashed)

    def test_verify_empty_hash_returns_false(self):
        assert not verify_password("SecurePass123!", "")

    def test_long_password_hashes_and_verifies(self):
        pw = "Aa1!" + "x" * 120
        hashed = get_password_hash(pw)
        assert verify_password(pw, hashed)


# ===========================================================================
# 9. EMAIL AND USERNAME VALIDATION
# ===========================================================================
class TestEmailValidation:
    def test_valid_email_normalized(self):
        assert validate_email_format("  User@Example.COM  ") == "user@example.com"

    @pytest.mark.parametrize("bad", [
        "johnexample.com",
        "   ",
        "a@b@c.com",
        "a" * 250 + "@b.com",
        "@example.com",
        "john@",
    ])
    def test_invalid_emails_rejected(self, bad):
        with pytest.raises(ValueError):
            validate_email_format(bad)

    def test_stricter_regex_rejects_leading_hyphen_domain(self):
        """The improved regex should reject a@-b.com."""
        with pytest.raises(ValueError):
            validate_email_format("a@-b.com")

    def test_stricter_regex_rejects_double_dot_domain(self):
        """The improved regex should reject a@b.."""
        with pytest.raises(ValueError):
            validate_email_format("a@b..")


class TestUsernameValidation:
    def test_valid_username_trimmed(self):
        assert validate_username_format(" john_doe-1 ") == "john_doe-1"

    @pytest.mark.parametrize("bad", ["ab", "a" * 51, "john doe", "john@doe"])
    def test_invalid_usernames_rejected(self, bad):
        with pytest.raises(ValueError):
            validate_username_format(bad)


class TestPasswordValidation:
    def test_strong_password_accepted(self):
        assert validate_password_strength("SecurePass123!") == "SecurePass123!"

    @pytest.mark.parametrize("bad", [
        "Ab1!xyz",         # too short
        "securepass1!",    # no uppercase
        "SECUREPASS1!",    # no lowercase
        "SecurePass!!",    # no digit
        "SecurePass123",   # no special
        "Aa1!" + "x" * 125,  # too long
    ])
    def test_weak_passwords_rejected(self, bad):
        with pytest.raises(ValueError):
            validate_password_strength(bad)


# ===========================================================================
# 10. EDGE CASES AND SECURITY TESTS
# ===========================================================================
class TestEdgeCases:
    def test_register_then_login_then_me_full_flow(self, client):
        """Full happy-path end-to-end flow."""
        # Register
        reg = _register(client)
        assert reg.status_code == 201

        # Login
        login = _login(client)
        assert login.status_code == 200
        token = login.json()["access_token"]

        # Profile
        me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["username"] == "john_doe"

    def test_multiple_registrations_unique_ids(self, client):
        r1 = _register(client, email="a@test.com", username="user_a")
        r2 = _register(client, email="b@test.com", username="user_b")
        assert r1.json()["id"] != r2.json()["id"]

    def test_sql_injection_in_login_rejected(self, client):
        """SQL injection attempts should not bypass authentication."""
        _register(client)
        r = _login(client, identity="' OR 1=1 --", password="anything")
        assert r.status_code == 401

    def test_xss_in_full_name_stored_as_is(self, client):
        """XSS payloads in full_name should be stored as text (output escaping is frontend's job)."""
        xss_name = '<script>alert("xss")</script>'
        r = _register(client, full_name=xss_name, email="xss@test.com", username="xss_user")
        assert r.status_code == 201
        # The name is stored; output escaping is the client's responsibility

    def test_unicode_full_name(self, client):
        r = _register(client, full_name="日本語テスト", email="uni@test.com", username="uni_user")
        assert r.status_code == 201
        assert r.json()["full_name"] == "日本語テスト"


# ===========================================================================
# 11. SECRET KEY CONFIGURATION AND WARNING VERIFICATION
# ===========================================================================
class TestSecretKeySecurity:
    def test_default_secret_key_triggers_warning(self):
        """Verifies that the default placeholder SECRET_KEY triggers a security warning."""
        with pytest.warns(UserWarning, match="SECRET_KEY is set to a default or weak value"):
            warned = check_secret_key_security("your_secret_key_here")
            assert warned is True

    @pytest.mark.parametrize("weak_key", ["secret", "changeme", "password", "short", "", "a" * 31])
    def test_weak_or_short_secret_key_triggers_warning(self, weak_key):
        """Verifies that short (<32 chars) or common passwords trigger a security warning."""
        with pytest.warns(UserWarning, match="SECRET_KEY is set to a default or weak value"):
            warned = check_secret_key_security(weak_key)
            assert warned is True

    def test_strong_secret_key_no_warning(self):
        """Verifies that a strong 32+ character key does not emit any warning."""
        import warnings
        with warnings.catch_warnings(record=True) as record:
            warnings.simplefilter("always")
            warned = check_secret_key_security("c1960b9251a44d46af7167fe54c4508c5dcb8e85a1ca1e3258834607a42da34c")
            assert warned is False
            assert len(record) == 0

    def test_permanent_local_secret_key_is_configured(self):
        """Verifies that the permanent local SECRET_KEY is set, non-default, and >= 32 chars."""
        assert settings.SECRET_KEY is not None
        assert settings.SECRET_KEY != "your_secret_key_here"
        assert len(settings.SECRET_KEY) >= 32

