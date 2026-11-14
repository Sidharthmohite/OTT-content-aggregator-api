# Module Descriptions

Status key: **Merged** = in `src/` on `main`; **Written, not connected** = code is in the repo but outside `src/`, so the app does not use it; **Placeholder** = file exists but is empty; **Planned** = not written yet. Everything marked here was read in the repo code by M6.

## 1. Application entry point (`src/main.py`)

Creates the FastAPI app ("OTT Content Aggregator API", version 1.0.0) with `GET /` (welcome message) and `GET /health` (`{"status": "healthy"}`). It also registers the titles router (M4). It does **not** register an auth router yet. Covered by `tests/test_health.py`.

## 2. Core module (`src/core/`), owner M3

| File | Purpose | Status |
|---|---|---|
| `config.py` | `Settings` class (pydantic-settings) reading `.env`: `PROJECT_NAME`, `VERSION`, `API_V1_STR`, `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REDIS_URL`. Defaults are placeholders. | Merged |
| `database.py` | SQLAlchemy engine, `SessionLocal`, `Base`, `get_db()` (one session per request, closed in `finally`) and `test_connection()` (returns `True`/`False`). `python -m src.core.database` tests the connection. | Merged |

Notes:
- No code turns a database failure into an HTTP 503. M3's written answer said it "should"; the code does not.
- `requirements.txt` lists two PostgreSQL drivers (`psycopg2-binary` and `psycopg[binary]`). To confirm with M3 which is used.

### Alembic (`alembic/`, `alembic.ini`), owner M3
`env.py`, `script.py.mako` and an empty `versions/` folder are merged. The only migration so far is M2's `001_create_users_table.py`, which sits in M2's folder. There is no migration for the `titles` table.

## 3. Titles: model, schemas, routes, service, owner M4

| File | Responsibility | Status |
|---|---|---|
| `src/models/title.py` | `Title` model, table `titles`: `id`, `title`, `description`, `content_type` (`movie` or `web_series`), `release_year`, `language`, `duration_minutes`, `number_of_seasons`, `created_at`. No link to genres or platforms yet. | Merged |
| `src/schemas/title.py` | `TitleCreate`, `TitleResponse`, `TitleUpdate` | Merged |
| `src/api/titles.py` | GET list, GET one, POST, PATCH, DELETE under `/titles` | Merged |
| `src/services/catalog_service.py` | `get_titles`, `get_title`, `create_title`, `update_title`, `delete_title` | Merged |
| `sample_data/` | `inception.json` (movie), `stranger_things.json` (web series) | Merged |

`TITLE_FIELDS.md` is at the repo root; it belongs in `docs/`.

## 4. Users and authentication, owner M2

All M2 files are in `M2_extracted_files/python project work M2/`, a copy of a whole project. The matching files inside `src/` (`src/models/user.py` etc.) are still empty.

| File (inside M2's folder) | Responsibility |
|---|---|
| `src/models/user.py` | `User` model, table `users`: `id`, `email` (unique), `username` (unique), `hashed_password`, `full_name`, `is_active`, `is_superuser`, `created_at`, `updated_at` |
| `src/schemas/user.py` | `UserCreate`, `UserUpdate`, `UserResponse`, `UserLogin`, `Token`, `TokenData`; email, username and password rules |
| `src/services/user_service.py` | `UserService`: create user (duplicate email/username checks), update user, authenticate user |
| `src/core/security.py` | Password hashing with passlib bcrypt (PBKDF2-SHA256 fallback), JWT create and decode |
| `src/api/routes/auth.py` | `POST /auth/register`, `POST /auth/login` |
| `alembic/versions/001_create_users_table.py` | Migration for the `users` table |
| `tests/` | `test_user_model.py`, `test_user_schemas.py`, `test_user_service.py`, `run_tests.py` (M2 reports 31 tests passing; not run by M6) |

Status: **written, not connected.** Details and error codes are in [API_ENDPOINTS.md](API_ENDPOINTS.md).

## 5. Genres and platforms, owner M5

`src/models/genre.py`, `platform.py`, `src/api/genres.py` and `platforms.py` are **empty placeholders**. No M5 code has been seen.

## 6. Team ownership overview

| Module | Owner | Status |
|---|---|---|
| Documentation and test planning | M6 | README, `docs/`, `tests/testing_checklist.md`, `tests/test_health.py` |
| Database config and Alembic | M3 | Merged |
| Titles | M4 | Merged |
| Users and authentication | M2 | Written, not connected |
| Genres and platforms | M5 | Placeholders only |

## 7. Open issues to resolve with the team

- **M2 code location.** It must move into `src/`, with the auth router added to `src/main.py`. M2's folder also has its own `config.py`, `database.py`, `main.py`, `alembic/` and `README.md`, which may conflict with M3's and M1's versions.
- **Dependencies.** M2's code imports `jwt` (PyJWT) and passlib, but `requirements.txt` on `main` lists neither. The project guide named python-jose, so the team should agree on one JWT library.
- **Written answers vs code.** M2's written answers described Node/MongoDB (a `role` and `watchlist` field, `/api/auth/...` routes, 24h/7d tokens). The real code is FastAPI: `username`, `is_superuser`, `/auth/...` routes, 30-minute tokens. These docs follow the code.
- **No protected routes yet.** `decode_access_token` exists, but nothing uses it.
- **Inactive users.** `authenticate_user` does not check `is_active`.
- **M2's own docs.** `M2_extracted_files/.../docs/MODULES.md` and `tests/testing_checklist.md` duplicate M6's files and show outdated statuses for other members.
- **M3.** Which PostgreSQL driver is used; whether a 503 handler is planned.
- **M4.** Move `TITLE_FIELDS.md` into `docs/`; decide on rules for language, duration and seasons; link titles to genres and platforms; generate a migration for `titles`.
- **M5.** Push genre and platform code.
