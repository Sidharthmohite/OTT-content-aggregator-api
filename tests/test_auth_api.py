"""Tests for M2's /auth/register and /auth/login endpoints.

Uses an in-memory SQLite database and its own small FastAPI app, so it works
even before the auth router is added to src/main.py.
Needs M2's code inside src/ (see docs/PROJECT_STATUS.md, integration steps).
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.core.security import decode_access_token
import src.models.user  # noqa: F401  (registers the users table)

try:
    from src.api.auth import router as auth_router
except ImportError:  # M2's original location
    from src.api.routes.auth import router as auth_router

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

USER = {
    "email": "john@example.com",
    "username": "john_doe",
    "password": "SecurePass123!",
    "full_name": "John Doe",
}


@pytest.fixture()
def client():
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


# ---------- register ----------
def test_register_success_hides_password(client):
    r = client.post("/auth/register", json=USER)
    assert r.status_code == 201
    body = r.json()
    assert body["username"] == "john_doe"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_lowercases_email(client):
    r = client.post("/auth/register", json={**USER, "email": "  John@Example.COM "})
    assert r.status_code == 201
    assert r.json()["email"] == "john@example.com"


def test_duplicate_email_returns_409(client):
    client.post("/auth/register", json=USER)
    r = client.post("/auth/register", json={**USER, "username": "other_user"})
    assert r.status_code == 409


def test_duplicate_email_different_case_returns_409(client):
    client.post("/auth/register", json=USER)
    r = client.post(
        "/auth/register",
        json={**USER, "email": "JOHN@EXAMPLE.COM", "username": "other_user"},
    )
    assert r.status_code == 409


def test_duplicate_username_returns_409(client):
    client.post("/auth/register", json=USER)
    r = client.post("/auth/register", json={**USER, "email": "other@example.com"})
    assert r.status_code == 409


@pytest.mark.parametrize(
    "change",
    [
        {"email": "not-an-email"},
        {"username": "ab"},
        {"username": "john doe"},
        {"password": "short1!"},
        {"password": "nouppercase1!"},
        {"password": "NOLOWERCASE1!"},
        {"password": "NoDigitsHere!"},
        {"password": "NoSpecial123"},
    ],
)
def test_invalid_registration_returns_422(client, change):
    assert client.post("/auth/register", json={**USER, **change}).status_code == 422


@pytest.mark.parametrize("missing", ["email", "username", "password"])
def test_missing_field_returns_422(client, missing):
    payload = {k: v for k, v in USER.items() if k != missing}
    assert client.post("/auth/register", json=payload).status_code == 422


# ---------- login ----------
def test_login_with_username(client):
    client.post("/auth/register", json=USER)
    r = client.post("/auth/login", json={"username_or_email": "john_doe", "password": USER["password"]})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    payload = decode_access_token(body["access_token"])
    assert payload["username"] == "john_doe"


def test_login_with_email(client):
    client.post("/auth/register", json=USER)
    r = client.post("/auth/login", json={"username_or_email": "JOHN@example.com", "password": USER["password"]})
    assert r.status_code == 200


def test_wrong_password_returns_401(client):
    client.post("/auth/register", json=USER)
    r = client.post("/auth/login", json={"username_or_email": "john_doe", "password": "WrongPass123!"})
    assert r.status_code == 401


def test_unknown_user_same_message_as_wrong_password(client):
    client.post("/auth/register", json=USER)
    wrong = client.post("/auth/login", json={"username_or_email": "john_doe", "password": "WrongPass123!"})
    unknown = client.post("/auth/login", json={"username_or_email": "nobody", "password": "WrongPass123!"})
    assert unknown.status_code == 401
    assert unknown.json() == wrong.json()


@pytest.mark.xfail(reason="authenticate_user does not check is_active")
def test_gap_inactive_user_cannot_login(client):
    client.post("/auth/register", json={**USER, "is_active": False})
    r = client.post("/auth/login", json={"username_or_email": "john_doe", "password": USER["password"]})
    assert r.status_code in (400, 401, 403)
