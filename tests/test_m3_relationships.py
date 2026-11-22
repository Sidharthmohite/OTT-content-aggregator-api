
"""M3 integration tests for many-to-many relationships and foreign keys."""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.core.database import Base
from src.models import Title, Genre, Platform
from src.models.associations import title_genres, title_platforms


@pytest.fixture
def test_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


def test_title_genre_platform_link_and_unlink(test_db):
    with Session(test_db) as db:
        title = Title(
            title="M3 Relationship Test",
            content_type="movie",
            release_year=2024,
            language="English",
        )

        genre = Genre(name="M3 Test Genre")
        platform = Platform(name="M3 Test Platform")

        title.genres.append(genre)
        title.platforms.append(platform)

        db.add(title)
        db.commit()

        title_id = title.id

        # Verify relationships persisted in the database.
        saved_title = db.get(Title, title_id)

        assert saved_title.genres[0].name == "M3 Test Genre"
        assert saved_title.platforms[0].name == "M3 Test Platform"

        # Unlink the relationships.
        saved_title.genres.remove(genre)
        saved_title.platforms.remove(platform)
        db.commit()

        # Verify unlinking persisted.
        db.refresh(saved_title)

        assert saved_title.genres == []
        assert saved_title.platforms == []


@pytest.mark.parametrize(
    "association_table",
    [title_genres, title_platforms],
    ids=["title_genres", "title_platforms"],
)
def test_invalid_foreign_key_rejected(test_db, association_table):
    with Session(test_db) as db:
        invalid_insert = association_table.insert().values(
            title_id=999999,
            **(
                {"genre_id": 999999}
                if association_table.name == "title_genres"
                else {"platform_id": 999999}
            ),
        )

        with pytest.raises(IntegrityError):
            db.execute(invalid_insert)
            db.commit()

        db.rollback()
