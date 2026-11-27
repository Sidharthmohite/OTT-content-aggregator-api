# M1 - Movie and Web Series Test Results

## Project
OTT Content Aggregator API

## Assigned Member
M1 - Siddharth Mohite

## 1. Movie API Tests

| Test Case | Expected Status | Actual Status | Result |
|---|---:|---:|---|
| Create Movie | 201 | 201 | PASS |
| Get All Movies | 200 | 200 | PASS |
| Get Movie By ID | 200 | 200 | PASS |
| Update Movie | 200 | 200 | PASS |
| Delete Movie | 200 | 200 | PASS |
| Get Deleted Movie | 404 | 404 | PASS |
| Invalid Movie ID | 404 | 404 | PASS |
| Empty Movie Title | 422 | 422 | PASS |
| Missing Required Fields | 422 | 422 | PASS |
| Invalid Release Year | 422 | 422 | PASS |
| Invalid Duration | 422 | 422 | PASS |
| Duplicate Movie Create | 409 | 409 | PASS |
| Duplicate Movie Update | 409 | 409 | PASS |

## 2. Web Series API Tests

| Test Case | Expected Status | Actual Status | Result |
|---|---:|---:|---|
| Create Web Series | 201 | 201 | PASS |
| Get All Web Series | 200 | 200 | PASS |
| Get Web Series By ID | 200 | 200 | PASS |
| Update Web Series | 200 | 200 | PASS |
| Delete Web Series | 200 | 200 | PASS |
| Get Deleted Web Series | 404 | 404 | PASS |
| Invalid Web Series ID | 404 | 404 | PASS |
| Empty Web Series Title | 422 | 422 | PASS |
| Missing Required Fields | 422 | 422 | PASS |
| Invalid Release Year | 422 | 422 | PASS |
| Invalid Number Of Seasons | 422 | 422 | PASS |
| Duplicate Web Series Create | 409 | 409 | PASS |
| Duplicate Web Series Update | 409 | 409 | PASS |

## 3. Database Verification

| Verification | Result |
|---|---|
| Movies table exists | PASS |
| Web Series table exists | PASS |
| Movie records persisted | PASS |
| Web Series records persisted | PASS |

Latest observed database row counts:
- Movies: 3
- Web Series: 3

## 4. Duplicate Validation Rule

A record is treated as duplicate when title, release year, and language match.
Title and language comparisons are case-insensitive.
Duplicate create and update requests return HTTP 409 Conflict.

## 5. Notes

- TestClient emitted a Starlette deprecation warning related to httpx.
- The warning did not prevent the tested API requests from passing.
- Database currently contains test records. They have not been cleaned up.

## 6. Overall Status

Movie CRUD: PASS
Web Series CRUD: PASS
Request Validation: PASS
Negative Testing: PASS
Duplicate Testing: PASS
Database Persistence: PASS

M1 documentation is prepared based on the tests executed so far.

## 7. Automated Test Results

Command:
`python -m unittest discover -s tests -p "test_*.py" -v`

| Test Module | Tests Passed | Failed | Result |
|---|---:|---:|---|
| Movie API (M1) | 13 | 0 | PASS |
| Web Series API (M1) | 13 | 0 | PASS |
| User Service (M2/Auth) | 11 | 0 | PASS |
| **Full Test Suite** | **37** | **0** | **PASS** |

Total execution time: 7.375 seconds.

All 37 automated tests passed successfully.
The Starlette/httpx deprecation warning did not affect test execution.
