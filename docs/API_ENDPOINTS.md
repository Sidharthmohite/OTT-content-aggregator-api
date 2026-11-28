# API Endpoint Documentation

See the [Week 1 verification](WEEK1_FINAL_VERIFICATION.md) and [Week 2 verification](WEEK2_GENRES_PLATFORMS.md) for test evidence.

## App basics

| Method | Endpoint | Success | Purpose |
| --- | --- | --- | --- |
| GET | `/` | 200 | Returns the welcome message |
| GET | `/health` | 200 | Returns `{"status": "healthy"}` |

The health endpoint reports application liveness.

## Movies and Web Series, owner M4

The titles router is defined in `src/api/titles.py` and registered in `src/main.py`.

| Method | Endpoint | Success | Errors | Purpose |
| --- | --- | --- | --- | --- |
| GET | `/titles/` | 200, list of titles | Validation errors where applicable | List titles |
| GET | `/titles/{title_id}` | 200 | 404 missing title; 422 invalid ID | Retrieve one title |
| POST | `/titles/` | 201 | 409 duplicate identity; 422 invalid input | Create a title |
| PATCH | `/titles/{title_id}` | 200 | 404 missing title; 409 duplicate identity; 422 invalid input | Update supplied fields |
| DELETE | `/titles/{title_id}` | 200 | 404 missing title; 422 invalid ID | Delete a title |

The collection path is `/titles/`. Item paths use `/titles/{title_id}`.

Title routes currently allow requests without an authentication token. Search, filtering, and API operations for linking genres and platforms remain pending.

### Title creation fields

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `title` | string | yes | 1 to 255 characters |
| `description` | string or null | no | Optional description |
| `content_type` | string | yes | `movie` or `web_series` |
| `release_year` | integer | yes | 1888 to 2100, inclusive |
| `language` | string | yes | Trimmed and must contain non-whitespace characters |
| `duration_minutes` | integer or null | no | Greater than zero when supplied; must be null or omitted for web series |
| `number_of_seasons` | integer or null | no | Greater than zero when supplied; must be null or omitted for movies |

`TitleResponse` includes these fields plus `id` and `created_at`.

### Create a movie

POST `/titles/`

```json
{
  "title": "Inception",
  "description": "A thief enters dreams.",
  "content_type": "movie",
  "release_year": 2010,
  "language": "English",
  "duration_minutes": 148
}
```

A successful request returns HTTP 201 and the created title.

### Create a web series

POST `/titles/`

```json
{
  "title": "Stranger Things",
  "content_type": "web_series",
  "release_year": 2016,
  "language": "English",
  "number_of_seasons": 4
}
```

### Partial updates

PATCH `/titles/{title_id}` accepts the fields to change. Title length is limited to 1–255 characters on both creation and update.

The service combines incoming fields with the stored record and validates the resulting data before saving. Conflicting movie and web-series fields return HTTP 422.

For example, update a movie's duration:

```json
{
  "duration_minutes": 95
}
```

When changing content type, clear the conflicting field in the same request. For example, convert a movie into a web-series record:

```json
{
  "content_type": "web_series",
  "duration_minutes": null,
  "number_of_seasons": 1
}
```

Rejected validation and duplicate updates preserve the stored record.

Existing records that violate the new content-specific rules require their conflicting fields to be corrected in the same PATCH request.

### Duplicate titles

A duplicate has the same case-sensitive combination of:

- `title`
- `content_type`
- `release_year`
- `language`

Different release years are allowed, supporting remakes with the same name.

The database enforces this rule through the `uq_titles_identity` constraint. Migration `9e811ea57f63` adds the constraint.

Duplicate POST and PATCH requests return HTTP 409:

```json
{
  "detail": "A title with the same name, content type, release year, and language already exists."
}
```

The service rolls back a duplicate-write transaction before returning the error.

### Missing titles

Requests for a missing title return HTTP 404:

```json
{
  "detail": "Title not found"
}
```

### Deletion

A successful DELETE returns HTTP 200:

```json
{
  "message": "Title deleted successfully"
}
```

## Users and Authentication, owner M2

The authentication router is defined in `src/api/auth.py` and registered in the main application.

| Method | Endpoint | Success | Errors | Purpose |
| --- | --- | --- | --- | --- |
| POST | `/auth/register` | 201, public user data | 409 duplicate email or username; 422 invalid input | Register a user |
| POST | `/auth/login` | 200, bearer token | 401 invalid credentials; 403 inactive account; 422 invalid input | Log in using JSON |
| POST | `/auth/token` | 200, bearer token | 401 invalid credentials; 403 inactive account; 422 invalid input | OAuth2 password-form login |
| GET | `/auth/me` | 200, public user data | 401 invalid or expired token; 403 inactive account; 404 missing user | Retrieve the authenticated profile |
| PATCH | `/auth/me` | 200, updated public user data | 401 unauthorized; 409 duplicate email or username; 422 invalid input | Update the authenticated profile |

Protected profile routes use bearer-token authentication.

### Registration fields

| Field | Required | Rules |
| --- | --- | --- |
| `email` | yes | Validated, trimmed, lowercased, maximum 255 characters, unique |
| `username` | yes | 3 to 50 characters; letters, numbers, underscores, and hyphens; unique |
| `password` | yes | 8 to 128 characters, including uppercase, lowercase, a digit, and a special character |
| `full_name` | no | Maximum 100 characters |
| `is_active` | no | Defaults to true |

The public user response contains `id`, `email`, `username`, `full_name`, `is_active`, `is_superuser`, `created_at`, and `updated_at`. Passwords and password hashes are excluded.

### JSON login

POST `/auth/login`

```json
{
  "username_or_email": "john_doe",
  "password": "SecurePass123!"
}
```

A successful login returns HTTP 200:

```json
{
  "access_token": "<access_token>",
  "token_type": "bearer"
}
```

The token contains the user ID in `sub` and the username. Expiration is controlled by `ACCESS_TOKEN_EXPIRE_MINUTES`, which defaults to 30 minutes.

Inactive accounts are rejected with HTTP 403.

### OAuth2 form login

POST `/auth/token` accepts password-form credentials using the `username` and `password` fields.

This endpoint supports Swagger UI's Authorize flow.

### Authenticated profile

GET `/auth/me` requires this header:

```http
Authorization: Bearer <access_token>
```

Example successful response:

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

PATCH `/auth/me` updates supported profile fields for the authenticated account.

## Genres and OTT Platforms, owner M5

Both collections use trailing slashes. Item paths use an integer ID.

| Method | Genre endpoint | Platform endpoint | Success | Errors |
| --- | --- | --- | --- | --- |
| GET | `/genres/` | `/platforms/` | 200 | |
| POST | `/genres/` | `/platforms/` | 201 | 409, 422 |
| GET | `/genres/{genre_id}` | `/platforms/{platform_id}` | 200 | 404, 422 |
| PATCH | `/genres/{genre_id}` | `/platforms/{platform_id}` | 200 | 404, 409, 422 |
| DELETE | `/genres/{genre_id}` | `/platforms/{platform_id}` | 200 | 404, 422 |

On creation, supply a nonblank `name`. Names are trimmed and case-sensitive, with a maximum of 100 characters for genres and 150 for platforms. Both accept an optional `description`. Platforms also accept an optional HTTP or HTTPS `website_url` up to 500 characters.

PATCH preserves omitted fields. Explicit null clears `description` or `website_url`. A null or blank name returns 422. A duplicate name returns 409 and preserves the stored record. Missing integer IDs return 404 and malformed IDs return 422.

DELETE returns a success message and removes the record and its title links while preserving the titles. These routes currently allow unauthenticated requests. See the [Week 2 verification](WEEK2_GENRES_PLATFORMS.md) for SQLite and PostgreSQL evidence.

## Background synchronization

| Method | Proposed endpoint | Status | Purpose |
| --- | --- | --- | --- |
| POST | `/sync` | Planned | Start a simulated catalog synchronization |

The final synchronization endpoint and implementation remain to be agreed.

## Testing and evidence

See the [Week 1 verification](WEEK1_FINAL_VERIFICATION.md) for title and authentication evidence and the [Week 2 verification](WEEK2_GENRES_PLATFORMS.md) for Genre and Platform evidence.

- [Testing report](WEEK1_TEST_REPORT.md)
- [Bug report](WEEK1_BUG_REPORT.md)
- [Live API evidence](WEEK1_API_EVIDENCE.md)

## OpenAPI follow-up

Genre and Platform item routes declare applicable 404 and 409 responses. The Week 2 CRUD suite checks these declarations.