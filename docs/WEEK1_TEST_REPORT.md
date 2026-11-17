# Week 1 Testing Report

| Run | Reference | Result |
| --- | --- | --- |
| Root automated suite | Windows, Python 3.14, merged `main` at `007e41d` | 67 passed, 9 expected failures, 0 unexpected failures, 9 warning occurrences |
| PostgreSQL migration | Local `ott_catalog` | Upgrade succeeded. Alembic reported `bdfe0e261206 (head)`. |
| Main app OpenAPI | Local application | `/auth/register` and `/auth/login` were present. |
| Live PostgreSQL API requests | Swagger UI | 11 live checks matched their expected outcomes, including the partial-update retest and the post-delete 404. See [live API evidence](WEEK1_API_EVIDENCE.md). |
| Standalone M2 suite | Extracted historical project | Included for reference. Outside the verified root run. |

The automated result is transcribed from the completed run. Auth and catalog endpoint tests use in-memory SQLite. The warning occurrences comprise one Starlette HTTPX deprecation and eight JWT key-length warnings.

```powershell
python -m pytest tests --import-mode=importlib -q -rx
```

## Passed coverage

| Script | Passed behavior |
| --- | --- |
| `tests/test_health.py` | Welcome endpoint and application liveness |
| `tests/test_auth_api.py` | Registration and login, duplicate accounts, invalid credentials and malformed requests |
| `tests/test_auth_validation.py` | User input validation, password handling and JWT round trips, malformed tokens and expiry |
| `tests/test_titles_api.py` | Title listing, creation, retrieval, updates, deletion, not-found handling and input validation |

## Expected failed cases

| Case | Observed gap |
| --- | --- |
| `test_gap_inactive_user_cannot_login` | Inactive accounts can authenticate. |
| `test_gap_loose_email_regex[a@b..]` | Invalid domain punctuation is accepted. |
| `test_gap_loose_email_regex[a@b.-]` | Invalid domain punctuation is accepted. |
| `test_gap_loose_email_regex[a@-b.com]` | Domain labels starting with a hyphen are accepted. |
| `test_gap_empty_language_rejected` | Empty language value is accepted. |
| `test_gap_movie_with_seasons_rejected` | A movie can have a season count. |
| `test_gap_series_with_duration_rejected` | A web series can have a movie runtime. |
| `test_gap_patch_title_too_long_rejected` | The update schema accepts a title over 255 characters. |
| `test_gap_duplicate_title_rejected` | Duplicate-title handling has no agreed or implemented uniqueness rule. |

The [bug report](WEEK1_BUG_REPORT.md) tracks open issues. All 11 live checks are documented in the [evidence report](WEEK1_API_EVIDENCE.md), and their screenshots are included.

## Test function inventory

Parameterized functions can produce multiple cases. Status below summarizes each function from the reported baseline run.

### `test_auth_api.py`

- `test_register_success_hides_password` â€” Passed
- `test_register_lowercases_email` â€” Passed
- `test_duplicate_email_returns_409` â€” Passed
- `test_duplicate_email_different_case_returns_409` â€” Passed
- `test_duplicate_username_returns_409` â€” Passed
- `test_invalid_registration_returns_422` â€” Passed
- `test_missing_field_returns_422` â€” Passed
- `test_login_with_username` â€” Passed
- `test_login_with_email` â€” Passed
- `test_wrong_password_returns_401` â€” Passed
- `test_unknown_user_same_message_as_wrong_password` â€” Passed
- `test_gap_inactive_user_cannot_login` â€” Expected failure

### `test_auth_validation.py`

- `test_email_is_trimmed_and_lowercased` â€” Passed
- `test_bad_emails_rejected` â€” Passed
- `test_gap_loose_email_regex` â€” Expected failure
- `test_username_valid_and_trimmed` â€” Passed
- `test_bad_usernames_rejected` â€” Passed
- `test_strong_password_accepted` â€” Passed
- `test_weak_passwords_rejected` â€” Passed
- `test_hash_and_verify` â€” Passed
- `test_same_password_gives_different_hashes` â€” Passed
- `test_long_password_hash_still_verifies` â€” Passed
- `test_token_roundtrip` â€” Passed
- `test_expired_and_invalid_tokens_return_none` â€” Passed

### `test_health.py`

- `test_home` â€” Passed
- `test_health` â€” Passed

### `test_titles_api.py`

- `test_create_movie_all_fields` â€” Passed
- `test_create_movie_required_fields_only` â€” Passed
- `test_create_web_series` â€” Passed
- `test_get_one_and_list` â€” Passed
- `test_patch_changes_only_given_fields` â€” Passed
- `test_delete_then_404` â€” Passed
- `test_missing_id_returns_404` â€” Passed
- `test_non_numeric_id_returns_422` â€” Passed
- `test_invalid_values_return_422` â€” Passed
- `test_missing_required_field_returns_422` â€” Passed
- `test_empty_body_returns_422` â€” Passed
- `test_gap_empty_language_rejected` â€” Expected failure
- `test_gap_movie_with_seasons_rejected` â€” Expected failure
- `test_gap_series_with_duration_rejected` â€” Expected failure
- `test_gap_patch_title_too_long_rejected` â€” Expected failure
- `test_gap_duplicate_title_rejected` â€” Expected failure
