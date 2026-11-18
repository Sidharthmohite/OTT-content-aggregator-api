# API Endpoint Documentation

Implemented routes are registered in the main FastAPI application.

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
- The list and create collection path is `/titles/`. Item paths use `/titles/{title_id}`.
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

Code: `src/api/auth.py`. The main app registers the auth router alongside the titles router. **Fully Implemented.**

| Method | Endpoint | Success | Errors | Purpose |
|---|---|---|---|---|
| POST | `/auth/register` | 201, user data (no password) | 409 duplicate email or username; 422 invalid data | Register a new user |
| POST | `/auth/login` | 200, `{"access_token": "...", "token_type": "bearer"}` | 401 invalid credentials; 403 inactive account; 422 | Log in with username or email (JSON) |
| POST | `/auth/token` | 200, `{"access_token": "...", "token_type": "bearer"}` | 401 invalid credentials; 403 inactive account; 422 | OAuth2 form-data login (Swagger UI Authorize button) |
| GET | `/auth/me` | 200, `UserResponse` | 401 invalid/expired token; 403 inactive account; 404 user not found | Get current authenticated user profile |
| PATCH | `/auth/me` | 200, updated `UserResponse` | 401 unauthorized; 409 duplicate email/username; 422 invalid data | Update current user profile |

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

The token holds the user id (`sub`) and `username`, and expires after `ACCESS_TOKEN_EXPIRE_MINUTES` (30 by default). Inactive users are rejected with HTTP 403.

### Profile Request (`GET /auth/me`)

Headers:
`Authorization: Bearer <access_token>`

Response (HTTP 200):
```json
{
  "id": 1,
  "email": "john@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2026-11-18T14:30:00Z",
  "updated_at": null
}
```

## Genres and OTT Platforms, owner M5

| Method | Endpoint | Status | Purpose |
|---|---|---|---|
| GET | `/genres` | Planned | List genres |
| POST | `/genres` | Planned | Create a genre (name should be unique) |
| GET | `/platforms` | Planned | List OTT platforms |
| POST | `/platforms` | Planned | Create a platform (name should be unique) |

Genre and platform models and join tables exist. The corresponding API modules are empty and no genre or platform router is registered.

## Background sync (Week 4)

| Method | Endpoint | Status | Purpose |
|---|---|---|---|
| POST | `/sync` (name to be agreed) | Planned | Start a simulated catalog sync |
