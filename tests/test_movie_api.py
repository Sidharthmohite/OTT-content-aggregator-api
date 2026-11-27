import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.main import app
from src.models import Movie, WebSeries


class TestMovieAPI(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )

        Base.metadata.create_all(bind=self.engine)

        self.TestSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        def override_get_db():
            db = self.TestSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def create_movie(self, title="Inception", year=2010, language="English"):
        return self.client.post(
            "/movies/",
            json={
                "title": title,
                "release_year": year,
                "language": language,
                "duration_minutes": 148
            }
        )

    def test_create_movie(self):
        response = self.create_movie()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "Inception")

    def test_get_all_movies(self):
        self.create_movie()
        response = self.client.get("/movies/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_movie_by_id(self):
        created = self.create_movie()
        movie_id = created.json()["id"]

        response = self.client.get(f"/movies/{movie_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], movie_id)

    def test_update_movie(self):
        created = self.create_movie()
        movie_id = created.json()["id"]

        response = self.client.patch(
            f"/movies/{movie_id}",
            json={"title": "Inception Updated"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Inception Updated")

    def test_delete_movie(self):
        created = self.create_movie()
        movie_id = created.json()["id"]

        response = self.client.delete(f"/movies/{movie_id}")
        self.assertEqual(response.status_code, 200)

        missing = self.client.get(f"/movies/{movie_id}")
        self.assertEqual(missing.status_code, 404)

    def test_movie_not_found(self):
        response = self.client.get("/movies/99999")
        self.assertEqual(response.status_code, 404)

    def test_empty_title_validation(self):
        response = self.client.post(
            "/movies/",
            json={
                "title": "",
                "release_year": 2010,
                "language": "English"
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_missing_required_fields(self):
        response = self.client.post(
            "/movies/",
            json={"title": "Inception"}
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_release_year(self):
        response = self.client.post(
            "/movies/",
            json={
                "title": "Old Movie",
                "release_year": 1800,
                "language": "English"
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_duration(self):
        response = self.client.post(
            "/movies/",
            json={
                "title": "Invalid Movie",
                "release_year": 2020,
                "language": "English",
                "duration_minutes": 0
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_duplicate_movie_create(self):
        first = self.create_movie()
        second = self.create_movie()

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 409)
        self.assertEqual(second.json()["detail"], "Movie already exists")

    def test_duplicate_movie_update(self):
        first = self.create_movie("Interstellar", 2014)
        second = self.create_movie("The Matrix", 1999)

        movie_id = second.json()["id"]

        response = self.client.patch(
            f"/movies/{movie_id}",
            json={
                "title": "Interstellar",
                "release_year": 2014,
                "language": "English"
            }
        )

        self.assertEqual(response.status_code, 409)

    def test_duplicate_movie_case_insensitive(self):
        self.create_movie("Inception", 2010, "English")

        response = self.create_movie("INCEPTION", 2010, "ENGLISH")
        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":
    unittest.main()
