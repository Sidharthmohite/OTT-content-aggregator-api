# Week 2: Genre and OTT Platform Management

## Implemented endpoints

| Method | Endpoint | Success | Errors |
| --- | --- | --- | --- |
| GET | /genres/ | 200 | |
| POST | /genres/ | 201 | 409 duplicate name, 422 invalid input |
| GET | /platforms/ | 200 | |
| POST | /platforms/ | 201 | 409 duplicate name, 422 invalid input |

## Validation and behavior

- Names are trimmed and must not be blank.
- Genre names allow up to 100 characters.
- Platform names allow up to 150 characters.
- Names use the existing case-sensitive database uniqueness rule.
- Platform website URLs are optional and must use HTTP or HTTPS.
- Lists are ordered by name and ID.
- These endpoints currently require no authentication.
- Title associations and update/delete endpoints are outside this implementation.

## Verified results

- New genre/platform API tests: 27 passed.
- Full automated suite: 212 passed, one tracked Starlette deprecation warning.
- API tests use isolated in-memory SQLite databases.
- PostgreSQL connection succeeded.
- Alembic revision: 9e811ea57f63 (head).
- Alembic check: No new upgrade operations detected.
- git diff --check reported no whitespace errors.

## Live API evidence

PostgreSQL endpoint status codes and screenshots have not yet been recorded
in this report. Automated API tests are recorded separately above.
