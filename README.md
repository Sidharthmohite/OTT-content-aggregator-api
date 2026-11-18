# OTT Content Aggregator API

FastAPI service for movie and web-series catalog CRUD, user registration, and JWT login. SQLAlchemy persists data in PostgreSQL. The application exposes a liveness endpoint at `/health`.

## Local setup

Run these commands from the repository root in Windows PowerShell.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

For an existing setup, edit your local `.env`. Start PostgreSQL and create an empty development database such as `ott_catalog`. Set `DATABASE_URL` and a locally generated `SECRET_KEY` in `.env`. Keep credentials out of Git.

```dotenv
DATABASE_URL=postgresql+psycopg://username:password@127.0.0.1:5432/ott_catalog
```

```powershell
python -m alembic upgrade head
python -m alembic current
python -m uvicorn src.main:app --reload
```

Open [Swagger UI](http://127.0.0.1:8000/docs). The initial revision `bdfe0e261206` creates the catalog, auth, and association tables. For the registered routes and request examples, see [API endpoints](docs/API_ENDPOINTS.md).

## Tests

```powershell
python -m pip install pytest httpx
python -m pytest tests --import-mode=importlib -q -rx
```

The merged baseline `007e41d` reported 67 passed, 9 expected failures, and 9 warning occurrences. Auth and catalog endpoint tests use in-memory SQLite. PostgreSQL migration and live API evidence are recorded separately in the [Week 1 testing report](docs/WEEK1_TEST_REPORT.md).

- [Module descriptions](docs/MODULES.md)
- [Week 1 bugs and pending issues](docs/WEEK1_BUG_REPORT.md)
- [Swagger screenshot checklist](docs/WEEK1_API_EVIDENCE.md)
- [Original testing checklist](tests/testing_checklist.md)

## Project scope

The app registers home, health, titles, registration, and login routes. Genre and platform models and association tables exist. Dedicated genre/platform endpoints, catalog search and filters, protected routes, Redis caching, and background sync are pending. Make changes on a branch and open a pull request targeting `main`.
