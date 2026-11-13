# OTT Content Aggregator API

A backend REST API that brings movie and web-series information into **one searchable catalog**. Instead of checking several streaming services, a user can search a single catalog to see a title's type, release year, genre and the OTT platform(s) it is listed on.

> **Scope note:** Background synchronization only *simulates* fetching data from external OTT platforms. No real OTT integrations or live availability data are used.

## Overview

Requests arrive at a FastAPI application, are validated with Pydantic schemas, handled by service (business-logic) functions, and stored/read through SQLAlchemy and PostgreSQL. Redis can cache selected read requests, and a background task simulates catalog syncing.

## Objectives

- Build a structured, maintainable REST API for titles, genres, platforms and users.
- Support search and filtering (name, genre, release year, platform).
- Protect user accounts with hashed passwords and JWT authentication.
- Demonstrate caching (Redis) and background data synchronization.
- Cover the API with automated tests (Pytest + HTTPX), targeting at least 80% of endpoints.

## Features

- Movie and web-series catalog (`content_type` is `movie` or `web_series`)
- Search by title name
- Genre filtering (Action, Comedy, Drama, Thriller, ...)
- Release-year filtering (single year or range)
- OTT platform information per title
- User registration and login
- Protected routes (JWT)
- Redis caching of frequently requested data
- Background synchronization (simulated)
- Automated tests with Pytest and HTTPX
- Interactive Swagger UI at `/docs`

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Main language |
| FastAPI | REST endpoints and interactive docs |
| PostgreSQL | Data storage |
| SQLAlchemy 2.0 | ORM / database models |
| Pydantic v2 | Request and response validation |
| Alembic | Database migrations |
| JWT | Token creation and verification (the guide names python-jose; M2's code uses PyJWT) |
| passlib (bcrypt) | Password hashing |
| Redis | Caching (Week 3) |
| Pytest + HTTPX | Automated API tests |
| Git + GitHub | Version control and collaboration |

## Folder Structure

```
.
├── alembic/                 # Database migrations (Alembic)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini              # Alembic configuration
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # API route files (genres.py, platforms.py, titles.py)
│   ├── core/                # config.py, database.py
│   ├── models/              # SQLAlchemy models (genre, platform, title, user)
│   ├── schemas/             # Pydantic schemas (genre, platform, title, user)
│   └── services/            # business logic (catalog_service.py)
├── tests/
│   ├── test_health.py
│   ├── test_titles_api.py
│   ├── test_auth_validation.py
│   ├── test_auth_api.py
│   └── testing_checklist.md
├── docs/
│   ├── API_ENDPOINTS.md
│   ├── MODULES.md
│   └── PROJECT_STATUS.md
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Not yet in `src/`: M2's authentication code (user model, schemas, service, `security.py` and the `/auth` routes) is currently in `M2_extracted_files/` and still has to be moved into `src/` and connected to `src/main.py`. The genre and platform files are empty placeholders, and `TITLE_FIELDS.md` is at the repo root. See [docs/MODULES.md](docs/MODULES.md) for the status of each module.

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Sidharthmohite/OTT-content-aggregator-api.git
cd OTT-content-aggregator-api

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows PowerShell: venv\Scripts\Activate.ps1
                                # Windows Command Prompt: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root by copying the template (**never commit it to GitHub**):

```bash
cp .env.example .env            # Windows: copy .env.example .env
```

Set your local database credentials in `.env`:

```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/ott_aggregator
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379/0
```

### Database setup

1. **Install and start PostgreSQL** (download from [postgresql.org](https://www.postgresql.org/download/); on macOS `brew install postgresql@14`; on Ubuntu `sudo apt install postgresql`).
2. **Create the database:**
   ```bash
   psql -U postgres
   ```
   ```sql
   CREATE DATABASE ott_aggregator;
   \q
   ```
3. **Verify the connection:**
   ```bash
   python -m src.core.database
   ```
   A success message means the app can reach PostgreSQL.
4. **Alembic migrations** keep the database in sync with the models in `src/models/`:
   ```bash
   alembic revision --autogenerate -m "Initial schema migration"   # create a migration
   alembic upgrade head                                            # apply migrations
   alembic current                                                 # show current version
   alembic downgrade -1                                            # roll back one step
   ```
   No migration file exists yet, so the tables are not created until one is generated and the models are imported in `alembic/env.py`.

## Running the FastAPI Application

```bash
uvicorn src.main:app --reload
```

- API base URL: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/health
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## Running Tests

From the project folder, with the virtual environment active:

```bash
pip install pytest httpx
python -m pytest tests
```

Use `tests` at the end so pytest only looks in this project. The title and auth tests use an in-memory SQLite database, so PostgreSQL is not needed. `test_auth_validation.py` and `test_auth_api.py` need M2's code inside `src/`. Tests marked `xfail` describe known gaps and will show as `XPASS` once fixed. See `tests/testing_checklist.md` for the full list of planned test cases.

## Documentation

- [API endpoint documentation](docs/API_ENDPOINTS.md)
- [Module descriptions](docs/MODULES.md)
- [Project status and to-do list](docs/PROJECT_STATUS.md)
- [Testing checklist](tests/testing_checklist.md)

## Project Status

| Area | Status |
|---|---|
| FastAPI app, `/` and `/health` | Done |
| Database config, session, Alembic setup (M3) | Done |
| Titles: model, schemas, CRUD endpoints, service (M4) | Done, no login required yet |
| User authentication: model, schemas, register and login (M2) | Written, not yet moved into `src/` or connected |
| Migrations | Users migration exists in M2's folder; no titles migration yet |
| Genres and platforms (M5) | Not started (empty files) |
| Protected routes | Not started |
| Search and filters, Redis caching, background sync | Not started |
| Tests | Health tests done; title and auth tests prepared |

Full details, review findings and the to-do list per member are in [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md).

## Four-Week Roadmap

| Week | Work | Progress |
|---|---|---|
| 1 | Project scaffolding, models, schemas, database setup, Alembic | Mostly done; genres and platforms missing |
| 2 | JWT authentication, registration/login, catalog CRUD, protected routes | Catalog CRUD done; auth written but not connected; no protected routes |
| 3 | Filtering by genre/year/platform, Redis caching | Not started |
| 4 | Background sync (BackgroundTasks or Celery), Pytest/HTTPX tests | Not started; health tests done |

## Team Workflow

- Work on feature branches, not directly on `main`.
- Make small commits with clear messages; review via pull requests.
- Pull the latest `main` before starting new work.
- Never commit passwords, secret keys, database credentials or `.env` files.
- Do not use spaces at the end of file names (they break checkouts on Windows).
