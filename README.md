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

- Movie and web-series catalog (type distinguishes Movie / Web Series)
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
| JWT / python-jose | Token creation and verification |
| passlib | Password hashing |
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
│   ├── api/                 # API route files
│   │   ├── __init__.py
│   │   ├── genres.py
│   │   ├── platforms.py
│   │   └── titles.py
│   ├── core/                # configuration and database setup
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── genre.py
│   │   ├── platform.py
│   │   ├── title.py
│   │   └── user.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── genre.py
│   │   ├── platform.py
│   │   ├── title.py
│   │   └── user.py
│   └── services/            # business logic
│       ├── __init__.py
│       └── catalog_service.py
├── tests/
│   └── testing_checklist.md
├── docs/
│   ├── API_ENDPOINTS.md
│   ├── MODULES.md
│   └── TITLE_FIELDS.md
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

**Planned, not yet in the repo** (from the project guide): `src/core/security.py` (password hashing and JWT), `src/services/auth_service.py`, and an auth route file (`/auth/register`, `/auth/login`). This section will be updated as they are added by their respective owners.

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Sidharthmohite/OTT-content-aggregator-api.git
cd OTT-content-aggregator-api

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root by copying the template (**never commit it to GitHub**):

```bash
cp .env.example .env
```

Configure your local database credentials and application settings in `.env`:

```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/ott_aggregator
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379/0
```

### Database setup

#### 1. Install and Start PostgreSQL
- **macOS (Homebrew):**
  ```bash
  brew install postgresql@14
  brew services start postgresql@14
  ```
- **Ubuntu/Debian:**
  ```bash
  sudo apt update && sudo apt install postgresql postgresql-contrib
  sudo systemctl start postgresql
  ```
- **Windows:**
  Download and install the interactive installer from [postgresql.org](https://www.postgresql.org/download/windows/).

#### 2. Create the Database
Log into PostgreSQL CLI and create the project database:
```bash
psql -U postgres
```
```sql
CREATE DATABASE ott_aggregator;
GRANT ALL PRIVILEGES ON DATABASE ott_aggregator TO postgres;
\q
```

#### 3. Verify Database Connection
Test connectivity to PostgreSQL using the database verification utility:
```bash
python -m src.core.database
```
If connection is established, you will see:
```
✓ Database connection successful!
```

#### 4. Run Alembic Migrations
Alembic manages database schema versioning and keeps PostgreSQL in sync with SQLAlchemy models (`src/models/`).

- **Generate a new migration script** (run whenever models are created or updated):
  ```bash
  alembic revision --autogenerate -m "Initial schema migration"
  ```
- **Apply migrations** to the database:
  ```bash
  alembic upgrade head
  ```
- **Check current migration version**:
  ```bash
  alembic current
  ```
- **Roll back the last migration** (if needed):
  ```bash
  alembic downgrade -1
  ```

## Running the FastAPI Application

```bash
uvicorn src.main:app --reload
```

- API base URL: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## Running Tests

```bash
pytest
```

See `tests/testing_checklist.md` for planned and active test cases.

## Documentation

- [API endpoint requirements](docs/API_ENDPOINTS.md)
- [Module descriptions](docs/MODULES.md)
- [Title Fields Specification](docs/TITLE_FIELDS.md)

## Four-Week Roadmap

| Week | Work |
|---|---|
| 1 | Project scaffolding, models, schemas, database setup, Alembic |
| 2 | JWT authentication, registration/login, catalog CRUD, protected routes |
| 3 | Filtering by genre/year/platform, Redis caching |
| 4 | Background sync (BackgroundTasks or Celery), Pytest/HTTPX tests |

## Team Workflow

- Work on feature branches, not directly on `main`.
- Make small commits with clear messages; review via pull requests.
- Pull the latest `main` before starting new work.
- Never commit passwords, secret keys, database credentials or `.env` files.




#m4
Movie & Web Series Catalog

Project Overview

The Movie & Web Series Catalog is a Python-based project designed to manage information about movies and web series.

Features

- Store movie and web series details.
- Manage title information.
- Store release year and language.
- Maintain movie duration and series seasons.
- Support JSON sample data.

Technologies Used

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JSON

Sample Data

- Inception (Movie)
- Stranger Things (Web Series)

Project Structure

- "src/models/" – Database models
- "src/schemas/" – Data validation schemas
- "sample_data/" – Sample JSON files
- "docs/" – Project documentation

Testing

Python syntax and JSON formatting can be checked using Python commands.

Status

Movie and Web Series Catalog assignment module.

