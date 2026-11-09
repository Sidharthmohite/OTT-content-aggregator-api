# API Endpoint Requirements (Initial Draft)

Status: **planned, not implemented.** Final route names, fields and access rules are to be agreed by the team.

## Auth / Users

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| POST | `/auth/register` | Register a user (name, unique email, password) | Public |
| POST | `/auth/login` | Authenticate and return a JWT access token | Public |
| GET | `/users/me` *(optional)* | Return the current user's profile | Required |

Requirements: email must be unique; passwords stored as hashes; duplicate email returns 400/409.

## Movies / Web Series (Titles)

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| GET | `/titles` | List titles; supports query filters | Public |
| GET | `/titles/{title_id}` | Get one title by ID | Public |
| POST | `/titles` | Create a movie or web series | Required |
| PUT/PATCH | `/titles/{title_id}` | Update a title | Required |
| DELETE | `/titles/{title_id}` | Delete a title | Required |

Query parameters for `GET /titles` (Week 3): `search` (name), `genre`, `release_year`, `year_from`, `year_to`, `platform`, `type` (Movie / Web Series).

Title fields: `title` (required), `type` (required: Movie / Web Series), `release_year` (required), `description` (optional), `genres` (list), `platforms` (list).

Responses: 200/201 success; 404 not found; 422 validation error; 401 unauthenticated.

## Genres

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| GET | `/genres` | List genres | Public |
| POST | `/genres` | Create a genre (name must be unique) | Required |

## OTT Platforms

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| GET | `/platforms` | List OTT platforms | Public |
| POST | `/platforms` | Create a platform (name must be unique) | Required |

## Background Sync (Week 4, simulated)

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| POST | `/sync` *(name TBD)* | Trigger a simulated catalog sync as a background task | Required |

## Example response (illustrative)

```json
{
  "title": "KGF Chapter 2",
  "type": "Movie",
  "release_year": 2022,
  "genre": "Action",
  "platforms": ["Example OTT Platform"]
}
```
