# OTT Content Aggregator API

FastAPI-based backend service for movie and web-series catalog management, user registration, authentication, genres, and platforms. The application uses SQLAlchemy ORM and PostgreSQL for database persistence.

## Features

- FastAPI backend with REST API endpoints
- PostgreSQL database integration
- SQLAlchemy ORM and database relationships
- Alembic database migrations
- User registration and JWT authentication
- Genre CRUD operations
- Platform CRUD operations
- Movie and web-series catalog models
- Input validation and error handling
- Database session management and transaction rollback
- SQLite-based isolated automated testing

## Technology Stack

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- JWT authentication
- Pytest
- SQLite (automated testing)

## Local Setup

Run the following commands from the repository root in Windows PowerShell.

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Update your local `.env` with the appropriate database URL and a locally generated secret key. Do not commit credentials.

Example database URL format:

```dotenv
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/ott_aggregator
```

### 4. Run database migrations

```powershell
python -m alembic upgrade head
python -m alembic current
```

### 5. Start the application

```powershell
python -m uvicorn src.main:app --reload --port 8000
```

Open Swagger UI:

http://127.0.0.1:8000/docs

## API Verification

### Genre API

Genre endpoints were tested against the PostgreSQL database using Swagger UI.

| Operation | Result |
|---|---:|
| Create Genre | 201 |
| Get All Genres | 200 |
| Get Genre by ID | 200 |
| Update Genre | 200 |
| Delete Genre | 200 |
| Invalid Genre ID | 404 |

The invalid ID response was verified:

```json
{
  "detail": "Genre not found"
}
```

### Database Verification

- PostgreSQL connectivity verified.
- Database tables and schema inspected.
- Model registration and relationships verified.
- Foreign-key constraints checked.
- Database CRUD operations verified.
- Transaction rollback tested.
- Database session closure verified after normal execution and exceptions.

## Testing

Install testing dependencies if needed:

```powershell
python -m pip install pytest httpx
```

### Run the complete test suite

```powershell
python -m pytest tests --import-mode=importlib
```

The `importlib` mode is used to avoid test-module import conflicts caused by duplicate test files in the extracted M2 folder.

### Latest recorded results

| Test Suite | Result |
|---|---:|
| Database session and transaction tests | 8 passed |
| Genre service tests | 9 passed |
| Genre & Platform CRUD regression tests | 35 passed |
| Full regression suite | 390 passed |

The full automated regression suite uses SQLite for isolated testing. PostgreSQL integration and live Genre API verification were performed separately.

Historical commit bad7e96 had 326 tests collected. The current project has 390 passing tests. These results are from different revisions and different test operations; the exact reason for the difference has not been established.

## Verification Documentation

- [API Endpoints](docs/API_ENDPOINTS.md)
- [M3 Integration & Database Verification Report](docs/M3_INTEGRATION_REPORT.md)
- [Week 1 Testing Report](docs/WEEK1_TEST_REPORT.md)
- [Module Descriptions](docs/MODULES.md)
- [Week 1 Bugs and Pending Issues](docs/WEEK1_BUG_REPORT.md)
- [Swagger Screenshot Checklist](docs/WEEK1_API_EVIDENCE.md)
- [Original Testing Checklist](tests/testing_checklist.md)

## Project Scope

The project provides backend APIs for catalog, user authentication, genres, and platforms. Further improvements and integrations may be developed through feature branches and pull requests.

Contributions should be made on a separate branch and submitted through a pull request targeting `main`. Do not merge without team review.