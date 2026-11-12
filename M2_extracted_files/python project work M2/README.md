# OTT Content Aggregator API

A backend REST API built with FastAPI, PostgreSQL, SQLAlchemy 2.0, and Pydantic that brings movie and web-series information into one searchable catalog. Users can discover where titles are available across various OTT streaming platforms.

---

## Project Structure

```
.
├── alembic/                 # Database migrations (Alembic)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_create_users_table.py
├── alembic.ini              # Alembic configuration
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Settings and environment variables
│   │   ├── database.py      # SQLAlchemy engine, SessionLocal, get_db
│   │   └── security.py      # Password hashing (bcrypt/pbkdf2) & JWT
│   ├── models/
│   │   ├── __init__.py      # Exports Base and models for Alembic
│   │   └── user.py          # User SQLAlchemy database model (M2)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py          # User Pydantic schemas (M2)
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py  # User CRUD, duplicate email handling (M2)
│   └── api/
│       ├── __init__.py
│       └── routes/
│           ├── __init__.py
│           └── auth.py      # Auth endpoints (/auth/register, /auth/login)
├── tests/
│   ├── __init__.py
│   ├── run_tests.py         # Dedicated test runner
│   ├── test_user_model.py   # Unit tests for User model
│   ├── test_user_schemas.py # Unit tests for User schemas & validations
│   ├── test_user_service.py # Unit tests for duplicate handling & CRUD
│   └── testing_checklist.md
├── docs/
│   └── MODULES.md           # Module assignments and progress
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- PostgreSQL
- Git

### 2. Setup Virtual Environment

```bash
# Clone the repository
git clone https://github.com/Sidharthmohite/OTT-content-aggregator-api.git
cd OTT-content-aggregator-api

# Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and set your credentials:
```bash
cp .env.example .env
```

### 4. Database Setup & Migrations
```bash
# Apply migrations with Alembic
alembic upgrade head
```

### 5. Running the API
```bash
uvicorn src.main:app --reload
```
Interactive API docs are available at `http://localhost:8000/docs`.

---

## Running Automated Tests

Run the full test suite with either standard Python or Pytest:

```bash
# Run with the project test runner (zero dependencies required):
python tests/run_tests.py

# Or run with unittest:
python -m unittest discover tests

# Or run with pytest:
pytest tests/ -v
```
All 31 unit tests cover:
- User SQLAlchemy model definitions and attributes.
- UserCreate, UserResponse, UserUpdate schemas and field validations.
- Email normalization (automatic lowercasing and trimming).
- Strict password complexity (min 8 chars, uppercase, lowercase, digit, special char).
- Duplicate email prevention and case-insensitive uniqueness checks.
- Duplicate username prevention.
- Safe serialization omitting passwords from responses.
