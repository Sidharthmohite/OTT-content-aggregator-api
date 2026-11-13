# Project Status Report (M6)

Based on the code in the repository on 13 Nov 2026 (`main` at commit `38412f4` plus M2's folder). Everything below was read from the real files.

## 1. Summary against the four-week roadmap

| Week | Planned work | Status |
|---|---|---|
| 1 | FastAPI scaffolding | Done (`src/main.py`, `/`, `/health`) |
| 1 | SQLAlchemy models | Titles done (M4). Users written but not in `src/` (M2). Genre and Platform not started (M5) |
| 1 | Pydantic schemas | Titles done. Users written, not in `src/`. Genre and Platform not started |
| 1 | Database setup | Done (M3: `config.py`, `database.py`) |
| 1 | Alembic migrations | Set up (M3). Only a users migration exists, in M2's folder. No titles migration |
| 2 | JWT auth, register, login | Written (M2), not connected to the app |
| 2 | Catalog CRUD | Done for titles (create, read, update, delete). No login required yet |
| 2 | Protected routes | Not started. A token decoder exists, but no route uses it |
| 3 | Filters by genre, year, platform; search | Not started |
| 3 | Redis caching | Not started (only a `REDIS_URL` setting exists) |
| 4 | Background sync | Not started |
| 4 | Pytest/HTTPX tests, 80% of endpoints | Started: health tests (M6). Test files for titles and auth are prepared (section 4) |

## 2. What is done, by module

**M3, database and configuration (merged):** `config.py` reads settings from `.env`. `database.py` has the engine, `SessionLocal`, `Base`, `get_db()` and `test_connection()`. Alembic is set up.

**M4, titles (merged):** `Title` model, three schemas, five endpoints (`GET /titles/`, `GET /titles/{id}`, `POST /titles/`, `PATCH /titles/{id}`, `DELETE /titles/{id}`), a service layer and two sample data files.

**M2, authentication (written, not connected):** user model, schemas with validation, service with duplicate checks, password hashing, JWT helpers, `/auth/register` and `/auth/login`, a users migration and 31 tests. All of it sits in `M2_extracted_files/`.

**M6, documentation and testing:** README, `docs/` (API endpoints, modules, this report), the testing checklist, `tests/test_health.py` and the new test files below.

## 3. Review findings

Severity: **High** = the app will not work or is unsafe; **Medium** = wrong behaviour in some cases; **Low** = cleanup.

| # | Severity | Finding | Owner |
|---|---|---|---|
| 1 | High | M2's code is outside `src/`. The real `src/models/user.py` and `src/schemas/user.py` are empty, and `main.py` has no auth router | M2 / M1 |
| 2 | High | No migration creates the `titles` table, and nothing calls `create_all`. On PostgreSQL the title endpoints will fail with "relation titles does not exist" until a migration is generated | M3 / M4 |
| 3 | High | `requirements.txt` has no PyJWT, passlib or bcrypt, but M2's code imports `jwt`. The app will not start once M2's code is added | M2 |
| 4 | High | `SECRET_KEY` has a public default value (`your_secret_key_here`). If `.env` is missing, tokens are signed with a key anyone can read. The app should refuse to start without a real key | M3 |
| 5 | Medium | `get_password_hash` silently falls back to PBKDF2 if bcrypt fails (for example a passlib and newer bcrypt version mismatch, or a password over 72 bytes). The fallback hides the failure. Check which scheme is really used and pin versions | M2 |
| 6 | Medium | Login does not check `is_active`, so a deactivated user can still log in | M2 |
| 7 | Medium | Title routes require no login, so anyone can create, edit and delete titles | M4 / M2 |
| 8 | Medium | Title rules are loose: empty `language` is accepted, a movie can have seasons, a series can have a duration, `PATCH` does not limit the title to 255 characters, and the same title can be created twice | M4 |
| 9 | Medium | Titles have no link to genres or platforms, so the core feature (platform per title) has no data model yet | M4 / M5 |
| 10 | Medium | A database failure is not handled. `get_db()` and the routes have no error handler, so a down database gives a plain 500 error. M3's written answer said 503 | M3 |
| 11 | Low | The email check accepts bad values such as `a@b..`, `a@b.-` and `a@-b.com` (tested). The comment says "RFC 5322", but the pattern is much looser | M2 |
| 12 | Low | `TITLE_FIELDS.md` is at the repo root instead of `docs/` | M4 |
| 13 | Low | `requirements.txt` lists both `psycopg2-binary` and `psycopg[binary]` | M3 |
| 14 | Low | M2's folder has its own `main.py`, `config.py`, `database.py`, `alembic/`, `README.md`, `docs/MODULES.md` and `testing_checklist.md`. They duplicate and may contradict the main project's files | M2 / M1 |
| 15 | Low | `test_connection()` prints errors instead of logging them | M3 |

## 4. Testing

### What was verified (M6, isolated check)
M2's validation and security logic was copied into a separate script and run. **36 of 36 checks behaved as expected.** This covered: email trimming and lowercasing; username and password rules, including every missing-character-class case; password hash and verify (salted, wrong and empty password rejected, malformed hashes rejected); token create and decode (correct payload, 30-minute lifetime, expired, tampered and garbage tokens rejected). It also confirmed finding 11. The check ran on the PBKDF2 fallback path, because passlib is not installed in that environment.

### What could not be run
The full app, the database and the HTTP endpoints were **not** run, because FastAPI, SQLAlchemy and Pydantic could not be installed in the review environment. The three test files below were written from the code and syntax-checked, but **not executed**. Run them on your machine and report failures; a failure may mean a test mistake as well as a code bug.

### Test files in `tests/`

| File | Needs | What it covers |
|---|---|---|
| `test_health.py` | merged code | `/` and `/health` (passing on M6's machine) |
| `test_titles_api.py` | merged code | all five title endpoints, valid and invalid data, missing fields, 404 cases, plus 5 "known gap" tests |
| `test_auth_validation.py` | M2 code in `src/` | email, username, password rules, hashing, tokens |
| `test_auth_api.py` | M2 code in `src/` | register, duplicate email and username (409), validation (422), login (200, 401) |

Tests marked `xfail` describe known gaps from the table above. They show as `xfailed` now and `XPASS` once the gap is fixed.

### How to run
```
python -m pip install -r requirements.txt pytest httpx
python -m pytest tests -v
```
To run only the files that work before integration:
```
python -m pytest tests/test_health.py tests/test_titles_api.py -v
```

## 5. To do, by owner

**M1 (team leader)**
- Decide how M2's code is merged (section 6) and review the pull requests.
- Make sure `.env` is never committed and that the app fails without a real `SECRET_KEY`.

**M2**
- Move the code into `src/` and add the auth router to `src/main.py`.
- Add PyJWT, passlib and bcrypt to `requirements.txt` and test which hashing scheme is used.
- Block inactive users at login.
- Add a "current user" dependency and a profile route.
- Remove the duplicate files in `M2_extracted_files/`.

**M3**
- Generate the titles migration and check that `alembic/env.py` imports all models.
- Decide on one PostgreSQL driver.
- Add database error handling and logging.
- Fail at startup if `SECRET_KEY` is not set.

**M4**
- Tighten the title rules (language, movie or series fields, title length on update, duplicates).
- Link titles to genres and platforms.
- Add search and filtering by name, genre, year range and platform (Week 3).
- Move `TITLE_FIELDS.md` into `docs/`.
- Protect create, update and delete with a token once M2's code is connected.

**M5**
- Write the genre and platform models, schemas and routes (`GET` and `POST`, unique names). The files are still empty.
- Add the many-to-many tables between titles, genres and platforms.

**Later weeks (whole team)**
- Redis caching (Week 3).
- Simulated background sync with `BackgroundTasks` (Week 4).
- Tests for the remaining endpoints, targeting 80% of endpoints (Week 4). Check coverage with `pip install pytest-cov` and `python -m pytest tests --cov=src`.

**M6 (you)**
- Run the new test files and record the results.
- Keep README, `MODULES.md`, `API_ENDPOINTS.md` and the checklist up to date after every merge.
- Write tests for genres, platforms, filtering, caching and sync as they arrive.

## 6. Steps to organise the code (agree with M1 and M2 first)

Do this on a new branch, for example `fix/integrate-m2`. It moves M2's files into the real project.

```
git checkout main
git pull
git checkout -b fix/integrate-m2
$p = "M2_extracted_files\python project work M2"
copy "$p\src\models\user.py"           src\models\user.py
copy "$p\src\schemas\user.py"          src\schemas\user.py
copy "$p\src\services\user_service.py" src\services\user_service.py
copy "$p\src\core\security.py"         src\core\security.py
copy "$p\src\api\routes\auth.py"       src\api\auth.py
copy "$p\alembic\versions\001_create_users_table.py" alembic\versions\
```

Then edit these by hand:
1. `src/main.py`: add `from src.api.auth import router as auth_router` and, after the titles router line, `app.include_router(auth_router)`.
2. `src/models/__init__.py`: add `from src.models.title import Title` and `from src.models.user import User`.
3. `alembic/env.py`: make sure it imports `src.models` so autogenerate sees both tables.
4. `requirements.txt`: add `PyJWT`, `passlib` and `bcrypt` (if passlib complains about bcrypt, pin `bcrypt==4.0.1`).
5. Do not copy M2's `config.py`, `database.py`, `main.py`, `alembic.ini` or `README.md`. M3's versions are the ones to keep.

Then test:
```
pip install -r requirements.txt
python -m pytest tests -v
alembic upgrade head
alembic revision --autogenerate -m "create titles table"
alembic upgrade head
uvicorn src.main:app --reload
```
Open http://127.0.0.1:8000/docs and try register, login and the title endpoints. After that, delete `M2_extracted_files/`, run `git status`, and open a pull request.
