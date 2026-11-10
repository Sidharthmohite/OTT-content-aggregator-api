# Testing Checklist – OTT Content Aggregator API

Mark each case `[x]` once a test is written and passing.

**Note:** The checklist includes both currently testable cases and planned tests. Do not mark a case as passing until it has actually been implemented and verified.

## Database & Core Configuration (M3)

- [ ] Configuration reads `DATABASE_URL` and app settings correctly from `.env`
- [ ] Database connection succeeds with valid credentials (`src.core.database.test_connection`)
- [ ] FastAPI database dependency `get_db` yields active session and closes it cleanly after request
- [ ] Alembic initializes and detects model metadata correctly for migrations

## Movie data

### Valid movie data
- [ ] Create a movie with all fields (title, type=Movie, release_year, description, genre, platform) returns 201
- [ ] Created movie can be fetched by ID with matching data
- [ ] Create a movie with only required fields returns 201

### Invalid movie data
- [ ] Empty title returns 422
- [ ] Invalid type (not Movie / Web Series) returns 422
- [ ] Release year is not a number or is unrealistic (negative, far future) returns 422
- [ ] Nonexistent genre or platform ID returns 404/422
- [ ] Get/update/delete a nonexistent title ID returns 404

## Web series data

### Valid web series data
- [ ] Create a web series (type=Web Series) with all fields returns 201
- [ ] Web series appears in `GET /titles` and filters by `type`
- [ ] Update a web series returns 200 with updated values

## Missing fields
- [ ] Missing title returns 422
- [ ] Missing type returns 422
- [ ] Missing release_year returns 422
- [ ] Register user without email returns 422
- [ ] Register user without password returns 422
- [ ] Create genre / platform without name returns 422
- [ ] Empty request body returns 422

## Duplicate user email
- [ ] Registering a new user succeeds
- [ ] Registering again with the same email returns 400/409
- [ ] Email comparison is case-insensitive (e.g. `A@x.com` vs `a@x.com`)
- [ ] Original user's data is unchanged after the failed attempt

## Duplicate genre name
- [ ] Creating a genre succeeds
- [ ] Creating the same genre name again returns 400/409
- [ ] Duplicate check is case-insensitive (e.g. `Action` vs `action`)
- [ ] Only one record exists in the database afterwards

## Database connection errors
- [ ] App handles unreachable PostgreSQL without crashing (clear 500/503 error, no stack trace leaked)
- [ ] Wrong database credentials in `.env` produce a clear startup error
- [ ] Request fails gracefully if the DB connection drops mid-request
- [ ] Session is rolled back and closed after a failed transaction
- [ ] App recovers once the database is available again

## Additional (later weeks)
- [ ] Login with valid credentials returns a token; invalid password returns 401
- [ ] Protected routes reject missing/invalid tokens with 401
- [ ] Filters: genre, release year/range, platform, name search
- [ ] Redis cache hit/miss behaviour; app works if Redis is down
- [ ] Background sync task runs and adds simulated titles
- [ ] Tests cover at least 80% of endpoints

## Current Implementation Status

Currently implemented:
- FastAPI application startup (`src/main.py`).
- `GET /` – Welcome endpoint.
- `GET /health` – Health-check endpoint.
- PostgreSQL database connectivity, connection pooling, SessionLocal, declarative Base, and `get_db` dependency (`src/core/database.py`).
- Application settings and environment configuration management with Pydantic v2 (`src/core/config.py`).
- Alembic database migration scaffolding and environment (`alembic.ini`, `alembic/env.py`).

Pending implementation and testing:
- Movie and web-series CRUD operations.
- Genre and platform management.
- User registration and authentication.
- Redis caching.
- Background synchronization.
