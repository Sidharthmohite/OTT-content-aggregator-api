import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.main import app


class TestWebSeriesAPI(unittest.TestCase):

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

    def create_web_series(
        self,
        title="Dark",
        year=2017,
        language="German",
        seasons=3
    ):
        return self.client.post(
            "/web-series/",
            json={
                "title": title,
                "release_year": year,
                "language": language,
                "number_of_seasons": seasons
            }
        )

    def test_create_web_series(self):
        response = self.create_web_series()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "Dark")

    def test_get_all_web_series(self):
        self.create_web_series()
        response = self.client.get("/web-series/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_web_series_by_id(self):
        created = self.create_web_series()
        series_id = created.json()["id"]

        response = self.client.get(f"/web-series/{series_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], series_id)

    def test_update_web_series(self):
        created = self.create_web_series()
        series_id = created.json()["id"]

        response = self.client.patch(
            f"/web-series/{series_id}",
            json={
                "title": "Dark Updated",
                "number_of_seasons": 4
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Dark Updated")
        self.assertEqual(response.json()["number_of_seasons"], 4)

    def test_delete_web_series(self):
        created = self.create_web_series()
        series_id = created.json()["id"]

        response = self.client.delete(f"/web-series/{series_id}")
        self.assertEqual(response.status_code, 200)

        missing = self.client.get(f"/web-series/{series_id}")
        self.assertEqual(missing.status_code, 404)

    def test_web_series_not_found(self):
        response = self.client.get("/web-series/99999")
        self.assertEqual(response.status_code, 404)

    def test_empty_title_validation(self):
        response = self.client.post(
            "/web-series/",
            json={
                "title": "",
                "release_year": 2017,
                "language": "German",
                "number_of_seasons": 3
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_missing_required_fields(self):
        response = self.client.post(
            "/web-series/",
            json={"title": "Dark"}
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_release_year(self):
        response = self.client.post(
            "/web-series/",
            json={
                "title": "Old Series",
                "release_year": 1800,
                "language": "English",
                "number_of_seasons": 2
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_number_of_seasons(self):
        response = self.client.post(
            "/web-series/",
            json={
                "title": "Invalid Series",
                "release_year": 2020,
                "language": "English",
                "number_of_seasons": 0
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_duplicate_web_series_create(self):
        first = self.create_web_series()
        second = self.create_web_series()

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 409)
        self.assertEqual(
            second.json()["detail"],
            "Web Series already exists"
        )

    def test_duplicate_web_series_update(self):
        first = self.create_web_series("Breaking Bad", 2008)
        second = self.create_web_series("Money Heist", 2017)

        series_id = second.json()["id"]

        response = self.client.patch(
            f"/web-series/{series_id}",
            json={
                "title": "Breaking Bad",
                "release_year": 2008,
                "language": "German"
            }
        )

        self.assertEqual(response.status_code, 409)

    def test_duplicate_web_series_case_insensitive(self):
        self.create_web_series("Dark", 2017, "German")

        response = self.create_web_series("DARK", 2017, "GERMAN")
        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":
    unittest.main()
