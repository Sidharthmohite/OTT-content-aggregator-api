"""Tests for title CRUD and validation using an in-memory SQLite database."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.main import app
import src.models.title  # noqa: F401


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

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

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


# Valid requests


def test_create_movie_all_fields(client):
    response = client.post("/titles/", json=MOVIE)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] >= 1
    assert body["title"] == "Inception"
    assert body["content_type"] == "movie"
    assert "created_at" in body


def test_create_movie_required_fields_only(client):
    payload = {
        field: MOVIE[field]
        for field in ("title", "content_type", "release_year", "language")
    }
    response = client.post("/titles/", json=payload)

    assert response.status_code == 201
    assert response.json()["description"] is None


def test_create_web_series(client):
    response = client.post("/titles/", json=SERIES)

    assert response.status_code == 201
    assert response.json()["number_of_seasons"] == 4


def test_get_one_and_list(client):
    movie_response = client.post("/titles/", json=MOVIE)
    series_response = client.post("/titles/", json=SERIES)

    assert movie_response.status_code == 201
    assert series_response.status_code == 201

    title_id = movie_response.json()["id"]
    response = client.get(f"/titles/{title_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Inception"

    listing = client.get("/titles/")
    assert listing.status_code == 200
    assert len(listing.json()) == 2


def test_patch_changes_only_given_fields(client):
    created = client.post("/titles/", json=MOVIE)
    assert created.status_code == 201

    original = created.json()
    response = client.patch(
        f"/titles/{original['id']}",
        json={"release_year": 2011},
    )

    assert response.status_code == 200
    assert response.json() == {**original, "release_year": 2011}


def test_delete_then_404(client):
    created = client.post("/titles/", json=MOVIE)
    assert created.status_code == 201

    url = f"/titles/{created.json()['id']}"
    assert client.delete(url).status_code == 200
    assert client.get(url).status_code == 404


# Missing records and invalid IDs


def test_missing_id_returns_404(client):
    assert client.get("/titles/999").status_code == 404
    assert client.patch(
        "/titles/999",
        json={"language": "Hindi"},
    ).status_code == 404
    assert client.delete("/titles/999").status_code == 404


def test_non_numeric_id_returns_422(client):
    assert client.get("/titles/abc").status_code == 422


# Required fields and field validation


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
    response = client.post("/titles/", json={**MOVIE, **change})
    assert response.status_code == 422


@pytest.mark.parametrize(
    "missing",
    ["title", "content_type", "release_year", "language"],
)
def test_missing_required_field_returns_422(client, missing):
    payload = {
        field: value
        for field, value in MOVIE.items()
        if field != missing
    }

    assert client.post("/titles/", json=payload).status_code == 422


def test_empty_body_returns_422(client):
    assert client.post("/titles/", json={}).status_code == 422


def test_gap_empty_language_rejected(client):
    response = client.post("/titles/", json={**MOVIE, "language": ""})
    assert response.status_code == 422


def test_gap_movie_with_seasons_rejected(client):
    response = client.post(
        "/titles/",
        json={**MOVIE, "number_of_seasons": 3},
    )
    assert response.status_code == 422


def test_gap_series_with_duration_rejected(client):
    response = client.post(
        "/titles/",
        json={**SERIES, "duration_minutes": 50},
    )
    assert response.status_code == 422


def test_gap_patch_title_too_long_rejected(client):
    created = client.post("/titles/", json=MOVIE)
    assert created.status_code == 201

    response = client.patch(
        f"/titles/{created.json()['id']}",
        json={"title": "x" * 300},
    )
    assert response.status_code == 422


# PATCH validates the stored record together with incoming changes.


@pytest.mark.parametrize(
    ("payload", "changes"),
    [
        (MOVIE, {"number_of_seasons": 3}),
        (SERIES, {"duration_minutes": 50}),
        (MOVIE, {"content_type": "web_series"}),
        (SERIES, {"content_type": "movie"}),
    ],
)
def test_patch_rejects_invalid_combination_without_saving(
    client, payload, changes
):
    created = client.post("/titles/", json=payload)
    assert created.status_code == 201

    original = created.json()
    url = f"/titles/{original['id']}"

    rejected = client.patch(url, json=changes)
    assert rejected.status_code == 422

    stored = client.get(url)
    assert stored.status_code == 200
    assert stored.json() == original


def test_patch_can_change_type_and_clear_conflicting_field(client):
    created = client.post("/titles/", json=MOVIE)
    assert created.status_code == 201

    url = f"/titles/{created.json()['id']}"
    changes = {
        "content_type": "web_series",
        "duration_minutes": None,
        "number_of_seasons": 1,
    }

    updated = client.patch(url, json=changes)

    assert updated.status_code == 200
    assert updated.json() == {**created.json(), **changes}

    stored = client.get(url)
    assert stored.status_code == 200
    assert stored.json() == updated.json()


# Duplicate identity uses title, content type, release year, and language.


def test_gap_duplicate_title_rejected(client):
    created = client.post("/titles/", json=MOVIE)
    assert created.status_code == 201

    duplicate = client.post("/titles/", json=MOVIE)
    assert duplicate.status_code == 409

    listing = client.get("/titles/")
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_duplicate_patch_returns_409_and_preserves_record(client):
    first = client.post("/titles/", json=MOVIE)
    second = client.post(
        "/titles/",
        json={**MOVIE, "release_year": 2011},
    )

    assert first.status_code == 201
    assert second.status_code == 201

    original = second.json()
    url = f"/titles/{original['id']}"

    duplicate = client.patch(url, json={"release_year": 2010})
    assert duplicate.status_code == 409

    stored = client.get(url)
    assert stored.status_code == 200
    assert stored.json() == original

    valid_update = client.patch(url, json={"release_year": 2012})
    assert valid_update.status_code == 200
    assert valid_update.json()["release_year"] == 2012

    stored = client.get(url)
    assert stored.status_code == 200
    assert stored.json() == valid_update.json()