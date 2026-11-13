# API Endpoint Documentation

Status key: **Implemented** = in `src/` on `main` and registered in `src/main.py`; **Written, not connected** = code is in the repo but not in `src/`, so the app does not use it yet; **Planned** = not written yet.

## App basics

| Method | Endpoint | Status | Purpose |
|---|---|---|---|
| GET | `/` | Implemented | Welcome message |
| GET | `/health` | Implemented | Returns `{"status": "healthy"}` |

## Movies / Web Series (Titles), owner M4

Code: `src/api/titles.py`, merged into `main`. The router is registered in `src/main.py`. **Implemented.**

| Method | Endpoint | Success | Errors | Purpose |
|---|---|---|---|---|
| GET | `/titles/` | 200, list of titles | none defined | List all titles |
| GET | `/titles/{title_id}` | 200 | 404 `Title not found` | Get one title |
| POST | `/titles/` | 201 | 422 validation error | Create a title |
| PATCH | `/titles/{title_id}` | 200 | 404, 422 | Update some fields of a title |
| DELETE | `/titles/{title_id}` | 200 `{"message": "Title deleted successfully"}` | 404 | Delete a title |

Notes:
- There is no `PUT`; updates use `PATCH` with only the fields to change.
- These routes are **not protected**: no login token is required yet.
- The paths end with a slash (`/titles/`). Calling `/titles` without it redirects.
- Not built yet: search by name, filtering by genre / year / platform, and linking a title to genres and platforms.

### Title fields (`TitleCreate`)

| Field | Type | Required | Rules |
|---|---|---|---|
| `title` | string | yes | 1 to 255 characters |
| `description` | string | no | free text |
| `content_type` | string | yes | only `movie` or `web_series` |
| `release_year` | integer | yes | 1888 to 2100 |
| `language` | string | yes | no length rule in the schema |
| `duration_minutes` | integer | no | greater than 0 |
| `number_of_seasons` | integer | no | greater than 0 |

`TitleResponse` adds `id` and `created_at`. `TitleUpdate` makes every field optional (same rules where given).

Example create request:
```json
{
  "title": "Inception",
  "content_type": "movie",
  "release_year": 2010,
  "language": "English",
  "duration_minutes": 148
}
```

## Users / Authentication, owner M2

Code: `M2_extracted_files/python project work M2/src/api/routes/auth.py`. **Written, not connected:** it is not inside `src/`, and `src/main.py` does not include the auth router. The routes below only work once M2 moves the code into `src/` and registers the router.

| Method | Endpoint | Success | Errors | Purpose |
|---|---|---|---|---|
| POST | `/auth/register` | 201, user data (no password) | 409 duplicate email or username; 422 invalid data | Register a user |
| POST | `/auth/login` | 200, `{"access_token": "...", "token_type": "bearer"}` | 401 `Invalid username/email or password.`; 422 | Log in with username or email |

### Register request (`UserCreate`)

| Field | Required | Rules |
|---|---|---|
| `email` | yes | valid format, trimmed and lowercased, max 255, must be unique |
| `username` | yes | 3 to 50 characters: letters, numbers, `_` and `-` only, must be unique |
| `password` | yes | 8 to 128 characters with an uppercase letter, a lowercase letter, a digit and a special character |
| `full_name` | no | max 100 characters |
| `is_active` | no | defaults to true |

The response (`UserResponse`) has `id`, `email`, `username`, `full_name`, `is_active`, `is_superuser`, `created_at`, `updated_at`. It never includes the password or its hash.

### Login request (`UserLogin`)

```json
{ "username_or_email": "john_doe", "password": "SecurePass123!" }
```

The token holds the user id (`sub`) and `username`, and expires after `ACCESS_TOKEN_EXPIRE_MINUTES` (30 by default).

Not built yet: any route that requires a token (no "current user" dependency exists), a profile route, and a route to update a user. `UserService.update_user` exists, but no endpoint uses it.

## Genres and OTT Platforms, owner M5

| Method | Endpoint | Status | Purpose |
|---|---|---|---|
| GET | `/genres` | Planned | List genres |
| POST | `/genres` | Planned | Create a genre (name should be unique) |
| GET | `/platforms` | Planned | List OTT platforms |
| POST | `/platforms` | Planned | Create a platform (name should be unique) |

`src/api/genres.py` and `src/api/platforms.py` exist in the repo, but no code from M5 has been confirmed yet.

## Background sync (Week 4)

| Method | Endpoint | Status | Purpose |
|---|---|---|---|
| POST | `/sync` (name to be agreed) | Planned | Start a simulated catalog sync |
