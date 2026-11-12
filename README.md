# OTT Content Aggregator API

A FastAPI backend for managing a catalog of movies and web series. A title stores its name, content type, release year, language, and optional description, runtime, and season count. The main app uses Pydantic for validation and SQLAlchemy for persistence.

## API endpoints

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/` | Returns the welcome message |
| GET | `/health` | Reports that the application is responding |
| GET | `/titles/` | Lists all titles |
| POST | `/titles/` | Creates a title and returns HTTP 201 |
| GET | `/titles/{title_id}` | Retrieves one title |
| PATCH | `/titles/{title_id}` | Updates the supplied fields |
| DELETE | `/titles/{title_id}` | Deletes a title and returns a confirmation |

Requests for a missing title ID return HTTP 404. The title API accepts `movie` and `web_series` as content types. Invalid request fields such as an out-of-range release year or a zero runtime return HTTP 422. The health endpoint checks application liveness only.

The root app currently exposes title CRUD. Genre and platform modules are placeholders. JWT authentication code is in the separate [M2 milestone folder](M2_extracted_files/python%20project%20work%20M2/README.md). Search and filtering, Redis caching, and simulated background synchronization are planned.

## Local setup

Run the commands below from the repository root with Python 3.10 or newer. On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

On macOS or Linux, activate with `source venv/bin/activate` and copy the template with `cp .env.example .env`. If a local `.env` already exists, edit it directly. Keep it out of Git.

Start PostgreSQL, create a local development database named `ott_aggregator`, and set `DATABASE_URL` in `.env` to match your local credentials. The explicit driver name selects Psycopg 3.

```dotenv
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/ott_aggregator
```

The root Alembic directory has no committed migration revisions. To create the catalog table in a fresh local development database, run:

```text
python -c "from src.main import app; from src.core.database import Base, engine; Base.metadata.create_all(engine)"
python -m uvicorn src.main:app --reload
```

This initializes missing tables from the current models. Schema upgrades for an existing database need an Alembic revision.

Open [Swagger UI](http://127.0.0.1:8000/docs) or view the [OpenAPI schema](http://127.0.0.1:8000/openapi.json).

## Smoke test

With the server running, use Swagger UI to check the API against a local development database.

1. Send `GET /health` and expect HTTP 200 with `{"status":"healthy"}`.
2. Send `POST /titles/` with the contents of [inception.json](sample_data/inception.json) or [stranger_things.json](sample_data/stranger_things.json). Expect HTTP 201 and save the returned ID.
3. Send `GET /titles/` and `GET /titles/{title_id}` to confirm the record is present.
4. Send `PATCH /titles/{title_id}` with `{"description":"Updated description"}` and expect HTTP 200 with the new description. Try `{"duration_minutes":0}` and expect HTTP 422.
5. Send `DELETE /titles/{title_id}` and expect HTTP 200. Fetch the deleted ID again and expect HTTP 404.

The root `tests/` folder contains a [test checklist](tests/testing_checklist.md). The separate M2 milestone includes its own authentication tests.

## Repository guide

| Path | Contents |
| --- | --- |
| `src/main.py` | FastAPI entry point and router registration |
| `src/api/` | Route definitions |
| `src/core/` | Settings and database session setup |
| `src/models/`, `src/schemas/` | SQLAlchemy models and Pydantic schemas |
| `src/services/` | Catalog persistence logic |
| `sample_data/` | Example title request bodies |
| `alembic/` | Migration scaffolding |

- [Title field specification](TITLE_FIELDS.md)
- [API requirements](docs/API_ENDPOINTS.md)
- [Module descriptions](docs/MODULES.md)
