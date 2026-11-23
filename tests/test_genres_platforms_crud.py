import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.main import app
from src.models.genre import Genre
from src.models.platform import Platform
from src.models.title import Title
from src.models.associations import title_genres, title_platforms
import src.models.user


@pytest.fixture()
def context():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    def override_get_db():
        with factory() as db:
            yield db

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client, factory
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
        engine.dispose()


@pytest.mark.parametrize("endpoint", ["/genres/", "/platforms/"])
def test_crud_workflow(context, endpoint):
    client, factory = context
    created = client.post(
        endpoint, json={"name": "Original", "description": "Keep"}
    )
    assert created.status_code == 201
    original = created.json()
    url = f"{endpoint}{original['id']}"

    assert client.get(url).json() == original

    updated = client.patch(url, json={"name": " Updated "})
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated"
    assert updated.json()["description"] == "Keep"

    with factory() as db:
        model = Genre if endpoint == "/genres/" else Platform
        assert db.get(model, original["id"]).name == "Updated"

    cleared = client.patch(url, json={"description": None})
    assert cleared.status_code == 200
    assert cleared.json()["description"] is None

    unchanged = client.patch(url, json={})
    assert unchanged.status_code == 200
    assert unchanged.json() == cleared.json()

    assert client.delete(url).status_code == 200
    assert client.get(url).status_code == 404
    assert client.delete(url).status_code == 404


@pytest.mark.parametrize("endpoint", ["/genres/", "/platforms/"])
@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_missing_record(context, endpoint, method):
    client, _ = context
    kwargs = {"json": {"name": "Changed"}} if method == "patch" else {}
    response = getattr(client, method)(endpoint + "999999", **kwargs)
    assert response.status_code == 404


@pytest.mark.parametrize("endpoint", ["/genres/", "/platforms/"])
@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_invalid_id(context, endpoint, method):
    client, _ = context
    kwargs = {"json": {"name": "Changed"}} if method == "patch" else {}
    response = getattr(client, method)(endpoint + "invalid", **kwargs)
    assert response.status_code == 422


@pytest.mark.parametrize("endpoint", ["/genres/", "/platforms/"])
@pytest.mark.parametrize("name", [None, "", "   ", 123])
def test_invalid_patch_preserves_record(context, endpoint, name):
    client, _ = context
    original = client.post(endpoint, json={"name": "Original"}).json()
    url = f"{endpoint}{original['id']}"

    assert client.patch(url, json={"name": name}).status_code == 422
    assert client.get(url).json() == original


@pytest.mark.parametrize(
    ("endpoint", "limit"),
    [("/genres/", 100), ("/platforms/", 150)],
)
def test_patch_name_length(context, endpoint, limit):
    client, _ = context
    created = client.post(endpoint, json={"name": "Original"}).json()
    url = f"{endpoint}{created['id']}"

    assert client.patch(
        url, json={"name": "x" * limit}
    ).status_code == 200
    assert client.patch(
        url, json={"name": "y" * (limit + 1)}
    ).status_code == 422
    assert client.get(url).json()["name"] == "x" * limit


@pytest.mark.parametrize("endpoint", ["/genres/", "/platforms/"])
def test_duplicate_patch_preserves_record_and_recovers(context, endpoint):
    client, _ = context
    assert client.post(
        endpoint, json={"name": "Taken"}
    ).status_code == 201
    original = client.post(endpoint, json={"name": "Original"}).json()
    url = f"{endpoint}{original['id']}"

    response = client.patch(
        url, json={"name": " Taken ", "description": "Must not save"}
    )
    assert response.status_code == 409
    assert client.get(url).json() == original

    assert client.patch(
        url, json={"name": "Recovered"}
    ).status_code == 200
    assert client.patch(
        url, json={"name": "Recovered"}
    ).status_code == 200


def test_platform_url_update_and_clear(context):
    client, _ = context
    created = client.post("/platforms/", json={"name": "Platform"}).json()
    url = f"/platforms/{created['id']}"

    updated = client.patch(
        url, json={"website_url": "https://example.com"}
    )
    assert updated.status_code == 200
    assert updated.json()["website_url"] == "https://example.com/"

    for invalid in ["not-a-url", "ftp://example.com", ""]:
        assert client.patch(
            url, json={"website_url": invalid}
        ).status_code == 422

    assert client.get(url).json() == updated.json()

    cleared = client.patch(url, json={"website_url": None})
    assert cleared.status_code == 200
    assert cleared.json()["website_url"] is None


@pytest.mark.parametrize(
    ("endpoint", "model", "relationship", "association"),
    [
        ("/genres/", Genre, "genres", title_genres),
        ("/platforms/", Platform, "platforms", title_platforms),
    ],
)
def test_deleting_linked_record_preserves_title(
    context, endpoint, model, relationship, association
):
    client, factory = context
    created = client.post(endpoint, json={"name": "Linked"}).json()

    with factory() as db:
        title = Title(
            title="Relationship test",
            content_type="movie",
            release_year=2026,
            language="English",
            duration_minutes=90,
        )
        getattr(title, relationship).append(db.get(model, created["id"]))
        db.add(title)
        db.commit()
        title_id = title.id

    with factory() as db:
        stored = db.get(Title, title_id)
        assert [item.id for item in getattr(stored, relationship)] == [
            created["id"]
        ]
        assert len(db.execute(select(association)).all()) == 1

    assert client.delete(
        f"{endpoint}{created['id']}"
    ).status_code == 200

    with factory() as db:
        stored = db.get(Title, title_id)
        assert stored is not None
        assert getattr(stored, relationship) == []
        assert db.get(model, created["id"]) is None
        assert db.execute(select(association)).all() == []


@pytest.mark.parametrize(
    ("association", "model", "foreign_key"),
    [
        (title_genres, Genre, "genre_id"),
        (title_platforms, Platform, "platform_id"),
    ],
)
@pytest.mark.parametrize("missing", ["title", "related"])
def test_invalid_foreign_keys_rejected(
    context, association, model, foreign_key, missing
):
    _, factory = context

    with factory() as db:
        title = Title(
            title="Foreign key test",
            content_type="movie",
            release_year=2026,
            language="English",
        )
        related = model(name="Existing")
        db.add_all([title, related])
        db.commit()

        values = {
            "title_id": 999999 if missing == "title" else title.id,
            foreign_key: 999999 if missing == "related" else related.id,
        }

        with pytest.raises(IntegrityError):
            db.execute(association.insert().values(**values))
            db.commit()

        db.rollback()
        assert db.execute(select(association)).all() == []


@pytest.mark.parametrize(
    "path", ["/genres/{genre_id}", "/platforms/{platform_id}"]
)
def test_openapi_item_errors(path):
    operations = app.openapi()["paths"][path]
    assert "404" in operations["get"]["responses"]
    assert {"404", "409", "422"} <= set(
        operations["patch"]["responses"]
    )
    assert "404" in operations["delete"]["responses"]
