import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.main import app
import src.models.genre
import src.models.platform
import src.models.title
import src.models.user


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine)

    def override_get_db():
        with testing_session() as db:
            yield db

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        engine.dispose()


@pytest.mark.parametrize("endpoint", ["/genres/", "/platforms/"])
def test_empty_list(client, endpoint):
    response = client.get(endpoint)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("endpoint", ["/genres/", "/platforms/"])
def test_create_and_list(client, endpoint):
    payload = {"name": "Drama", "description": "Test description"}
    response = client.post(endpoint, json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] >= 1
    assert body["name"] == payload["name"]
    assert body["description"] == payload["description"]

    listing = client.get(endpoint)
    assert listing.status_code == 200
    assert listing.json() == [body]


@pytest.mark.parametrize("endpoint", ["/genres/", "/platforms/"])
def test_name_is_trimmed(client, endpoint):
    response = client.post(endpoint, json={"name": "  Drama  "})
    assert response.status_code == 201
    assert response.json()["name"] == "Drama"


@pytest.mark.parametrize("endpoint", ["/genres/", "/platforms/"])
@pytest.mark.parametrize("name", ["", "   ", None, 123])
def test_invalid_name(client, endpoint, name):
    response = client.post(endpoint, json={"name": name})
    assert response.status_code == 422
    assert client.get(endpoint).json() == []


@pytest.mark.parametrize("endpoint", ["/genres/", "/platforms/"])
def test_missing_name(client, endpoint):
    assert client.post(endpoint, json={}).status_code == 422


@pytest.mark.parametrize(
    ("endpoint", "limit"),
    [("/genres/", 100), ("/platforms/", 150)],
)
def test_name_length_boundary(client, endpoint, limit):
    assert client.post(
        endpoint, json={"name": "x" * limit}
    ).status_code == 201

    assert client.post(
        endpoint, json={"name": "y" * (limit + 1)}
    ).status_code == 422

    assert len(client.get(endpoint).json()) == 1


@pytest.mark.parametrize("endpoint", ["/genres/", "/platforms/"])
def test_duplicate_rejected_and_next_create_succeeds(client, endpoint):
    first = client.post(endpoint, json={"name": "Drama"})
    assert first.status_code == 201

    duplicate = client.post(endpoint, json={"name": " Drama "})
    assert duplicate.status_code == 409
    assert "detail" in duplicate.json()

    second = client.post(endpoint, json={"name": "Comedy"})
    assert second.status_code == 201

    listing = client.get(endpoint)
    assert listing.status_code == 200
    assert [item["name"] for item in listing.json()] == ["Comedy", "Drama"]


def test_platform_website_is_stored(client):
    response = client.post(
        "/platforms/",
        json={
            "name": "Netflix",
            "website_url": "https://www.netflix.com",
        },
    )
    assert response.status_code == 201
    assert response.json()["website_url"] == "https://www.netflix.com/"

    listing = client.get("/platforms/")
    assert listing.status_code == 200
    assert listing.json() == [response.json()]


@pytest.mark.parametrize(
    "url",
    ["not-a-url", "ftp://example.com", ""],
)
def test_invalid_platform_website(client, url):
    response = client.post(
        "/platforms/",
        json={"name": "Netflix", "website_url": url},
    )
    assert response.status_code == 422
    assert client.get("/platforms/").json() == []


def test_platform_website_can_be_omitted(client):
    response = client.post("/platforms/", json={"name": "Netflix"})
    assert response.status_code == 201
    assert response.json()["website_url"] is None


@pytest.mark.parametrize("endpoint", ["/genres/", "/platforms/"])
def test_openapi_declares_create_errors(endpoint):
    responses = app.openapi()["paths"][endpoint]["post"]["responses"]
    assert {"201", "409", "422"} <= set(responses)
