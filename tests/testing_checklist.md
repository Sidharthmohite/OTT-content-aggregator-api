# Testing Checklist

Mark a case `[x]` once a test for it is written and passing.
Field names and rules come from M4's title code (`src/schemas/title.py`, `src/models/title.py`) and M2's auth code (`M2_extracted_files/.../src/`, not yet connected to the app).
M2 reports 31 existing tests (`test_user_schemas.py`, `test_user_model.py`, `test_user_service.py`) in their folder. Not run by M6 yet.

## Already tested (tests/test_health.py)
- [x] `GET /` returns 200 and a `message`
- [x] `GET /health` returns 200 and `{"status": "healthy"}`
- [ ] `/docs` opens the Swagger page

## Valid movie data (`POST /titles/`)
- [ ] All fields (title, content_type=`movie`, release_year, language, description, duration_minutes) returns 201 with `id` and `created_at`
- [ ] Only required fields (title, content_type, release_year, language) returns 201
- [ ] `GET /titles/{id}` returns the same data that was created
- [ ] `GET /titles/` includes the new movie
- [ ] `PATCH /titles/{id}` changes only the given field and keeps the others
- [ ] `DELETE /titles/{id}` returns 200, then `GET` returns 404

## Invalid movie data
- [ ] Empty `title` returns 422
- [ ] `title` longer than 255 characters returns 422
- [ ] `content_type` not `movie` or `web_series` (e.g. `"Movie"`, `"film"`) returns 422
- [ ] `release_year` below 1888 or above 2100 returns 422
- [ ] `release_year` as text returns 422
- [ ] `duration_minutes` of 0 or negative returns 422
- [ ] `GET`, `PATCH` or `DELETE` with an ID that does not exist returns 404
- [ ] `GET /titles/abc` (non-numeric ID) returns 422

## Valid web series data
- [ ] All fields with content_type=`web_series` and `number_of_seasons` returns 201
- [ ] Web series appears in `GET /titles/`
- [ ] `PATCH` can update `number_of_seasons`

## Missing fields
- [ ] Missing `title` returns 422
- [ ] Missing `content_type` returns 422
- [ ] Missing `release_year` returns 422
- [ ] Missing `language` returns 422
- [ ] Empty request body returns 422
- [ ] `number_of_seasons` of 0 or negative returns 422

## Edge cases to ask M4 about (not enforced by the code)
- [ ] Empty `language` (`""`) is currently accepted
- [ ] A movie with `number_of_seasons`, or a web series with `duration_minutes`, is currently accepted
- [ ] `PATCH` with a `title` over 255 characters is not rejected by the schema
- [ ] Creating the same title twice is allowed (no unique rule)

## Registration (`POST /auth/register`, M2 code, not connected yet)
- [ ] Valid email, username and password returns 201 and no password or hash in the response
- [ ] Email is saved trimmed and in lowercase
- [ ] Invalid email format returns 422
- [ ] Username shorter than 3, longer than 50, or with spaces/symbols returns 422
- [ ] Password shorter than 8 returns 422
- [ ] Password missing an uppercase letter, lowercase letter, digit or special character returns 422
- [ ] Missing email, username or password returns 422
- [ ] Whitespace-only `full_name` is stored as empty (None)

## Duplicate user email
- [ ] Register a new user succeeds
- [ ] Register again with the same email returns 409
- [ ] Same email in different case (`A@x.com` vs `a@x.com`) returns 409
- [ ] Same username with a different email returns 409
- [ ] The first user's data is unchanged after the failed attempt

## Login (`POST /auth/login`)
- [ ] Correct username and password returns 200 with `access_token` and `token_type`
- [ ] Correct email and password also works
- [ ] Wrong password returns 401
- [ ] Unknown user returns 401 with the same message as a wrong password
- [ ] The token contains the user's id and username and expires after the configured minutes
- [ ] A deactivated user (`is_active` false) cannot log in. The current code does not check this, so it probably still logs in; ask M2

## Protected routes (not built yet)
- [ ] A protected route returns 401 without a token
- [ ] A protected route returns 401 with an invalid or expired token

## Duplicate genre name (M5, not built yet)
- [ ] Create a genre succeeds
- [ ] Create the same genre name again is rejected (error code to be confirmed)
- [ ] The check ignores upper/lower case
- [ ] Only one record exists afterwards

## Database connection errors (M3 code exists: `src/core/database.py`)
- [ ] `test_connection()` returns `True` when PostgreSQL is running with correct credentials
- [ ] `test_connection()` returns `False` with a wrong password or when PostgreSQL is stopped
- [ ] `get_db()` closes the session after a request, also after an error
- [ ] A title endpoint with the database down: record the current behaviour. The code has no error handler, so it probably returns 500, not 503
- [ ] Alembic runs after PostgreSQL is available: `alembic upgrade head`
- [ ] The `titles` table exists after migrations (no migration file is on the branch yet)

## Later weeks
- [ ] Filters: genre, release year or range, platform, name search
- [ ] Redis cache hit and miss; app still works if Redis is down
- [ ] Background sync runs and adds simulated titles
- [ ] Tests cover at least 80% of endpoints
