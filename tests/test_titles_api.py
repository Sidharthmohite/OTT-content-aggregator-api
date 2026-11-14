"""Tests for the title endpoints (M4): /titles/

Uses an in-memory SQLite database, so PostgreSQL is not needed.
Run from the project folder:  python -m pytest tests -v
Tests marked xfail describe gaps found in review; they will show XPASS once fixed.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.main import app
import src.models.title  # noqa: F401  (registers the titles table)

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

MOVIE = {
    "title": "Inception",
    "description": "A thief enters dreams.",
    "content_type": "movie",
    "release_year": 2010,
    "language": "English",
    "duration_minutes": 148,
}
SERIES = {
    "title": "Stranger Things",
    "content_type": "web_series",
    "release_year": 2016,
    "language": "English",
    "number_of_seasons": 4,
}


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------- valid data ----------
def test_create_movie_all_fields(client):
    r = client.post("/titles/", json=MOVIE)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] >= 1
    assert body["title"] == "Inception"
    assert body["content_type"] == "movie"
    assert "created_at" in body


def test_create_movie_required_fields_only(client):
    payload = {k: MOVIE[k] for k in ("title", "content_type", "release_year", "language")}
    r = client.post("/titles/", json=payload)
    assert r.status_code == 201
    assert r.json()["description"] is None


def test_create_web_series(client):
    r = client.post("/titles/", json=SERIES)
    assert r.status_code == 201
    assert r.json()["number_of_seasons"] == 4


def test_get_one_and_list(client):
    created = client.post("/titles/", json=MOVIE).json()
    client.post("/titles/", json=SERIES)
    one = client.get(f"/titles/{created['id']}")
    assert one.status_code == 200
    assert one.json()["title"] == "Inception"
    listing = client.get("/titles/")
    assert listing.status_code == 200
    assert len(listing.json()) == 2


def test_patch_changes_only_given_fields(client):
    created = client.post("/titles/", json=MOVIE).json()
    r = client.patch(f"/titles/{created['id']}", json={"release_year": 2011})
    assert r.status_code == 200
    assert r.json()["release_year"] == 2011
    assert r.json()["title"] == "Inception"


def test_delete_then_404(client):
    created = client.post("/titles/", json=MOVIE).json()
    assert client.delete(f"/titles/{created['id']}").status_code == 200
    assert client.get(f"/titles/{created['id']}").status_code == 404


# ---------- not found ----------
def test_missing_id_returns_404(client):
    assert client.get("/titles/999").status_code == 404
    assert client.patch("/titles/999", json={"language": "Hindi"}).status_code == 404
    assert client.delete("/titles/999").status_code == 404


def test_non_numeric_id_returns_422(client):
    assert client.get("/titles/abc").status_code == 422


# ---------- invalid / missing fields ----------
@pytest.mark.parametrize(
    "change",
    [
        {"title": ""},
        {"title": "x" * 256},
        {"content_type": "Movie"},
        {"content_type": "film"},
        {"release_year": 1700},
        {"release_year": 2101},
        {"release_year": "abc"},
        {"duration_minutes": 0},
        {"duration_minutes": -5},
        {"number_of_seasons": 0},
    ],
)
def test_invalid_values_return_422(client, change):
    r = client.post("/titles/", json={**MOVIE, **change})
    assert r.status_code == 422


@pytest.mark.parametrize("missing", ["title", "content_type", "release_year", "language"])
def test_missing_required_field_returns_422(client, missing):
    payload = {k: v for k, v in MOVIE.items() if k != missing}
    assert client.post("/titles/", json=payload).status_code == 422


def test_empty_body_returns_422(client):
    assert client.post("/titles/", json={}).status_code == 422


# ---------- known gaps (expected to fail until fixed) ----------
@pytest.mark.xfail(reason="language has no min length; empty string is accepted")
def test_gap_empty_language_rejected(client):
    r = client.post("/titles/", json={**MOVIE, "language": ""})
    assert r.status_code == 422


@pytest.mark.xfail(reason="a movie with number_of_seasons is accepted")
def test_gap_movie_with_seasons_rejected(client):
    r = client.post("/titles/", json={**MOVIE, "number_of_seasons": 3})
    assert r.status_code == 422


@pytest.mark.xfail(reason="a web series with duration_minutes is accepted")
def test_gap_series_with_duration_rejected(client):
    r = client.post("/titles/", json={**SERIES, "duration_minutes": 50})
    assert r.status_code == 422


@pytest.mark.xfail(reason="TitleUpdate.title has no max_length (database column is 255)")
def test_gap_patch_title_too_long_rejected(client):
    created = client.post("/titles/", json=MOVIE).json()
    r = client.patch(f"/titles/{created['id']}", json={"title": "x" * 300})
    assert r.status_code == 422


@pytest.mark.xfail(reason="no unique rule: the same title can be created twice")
def test_gap_duplicate_title_rejected(client):
    client.post("/titles/", json=MOVIE)
    assert client.post("/titles/", json=MOVIE).status_code in (400, 409)
