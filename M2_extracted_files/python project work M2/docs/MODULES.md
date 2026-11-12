# Team Module Assignments & Progress

| Member | Area | Week 1 Responsibilities | Status |
|---|---|---|---|
| **M1** | Team Leader | Repository setup, coordination, PR review, documentation | Completed |
| **M2** | User Model & Auth | User SQLAlchemy model, UserCreate/UserResponse/UserUpdate schemas, email & field validation, duplicate email handling, security helpers | **Completed** |
| **M3** | Database Management | PostgreSQL configuration, SQLAlchemy connection, SessionLocal, Alembic migrations setup | Completed / In PR #2 |
| **M4** | Title Catalog | Movie and web-series database model & schemas | In Progress |
| **M5** | Genre & Platform | Genre and Platform database models & schemas | In Progress |
| **M6** | Schema Consistency & QA | Schema review, testing plan, automated test suite | In Progress |

---

## Member M2 — User Model & Authentication Preparation

### Delivered Components:
1. **User SQLAlchemy Model (`src/models/user.py`)**:
   - Mapped to `users` table.
   - Primary key `id` (autoincrement, indexed).
   - `email` (unique index, max 255 chars, lowercase normalized).
   - `username` (unique index, max 50 chars).
   - `hashed_password` (secure hash storage, passwords never stored in plain text).
   - `full_name` (optional, max 100 chars).
   - `is_active` (boolean, default `True`).
   - `is_superuser` (boolean, default `False`).
   - `created_at` and `updated_at` (server default timestamps).
   - Human-readable `__repr__` method.

2. **User Pydantic Schemas (`src/schemas/user.py`)**:
   - `UserBase`: Common attributes with RFC 5322 email regex and username validation.
   - `UserCreate`: Registration schema with strict password complexity requirements (minimum 8 characters, uppercase, lowercase, number, special character).
   - `UserResponse`: Safe public representation excluding passwords and hashes (`model_config = ConfigDict(from_attributes=True)`).
   - `UserUpdate`: Optional field updates for user profile modification.
   - `UserLogin`, `Token`, `TokenData`: Prepared authentication schemas for Week 2 JWT integration.

3. **Email & Field Validation**:
   - Automatic trimming of whitespace.
   - Automatic normalization of emails to lowercase (prevents duplicate accounts due to casing differences).
   - Strict username rules: 3-50 characters, letters, numbers, underscores, and hyphens only.
   - Password strength validation with descriptive error feedback.

4. **Duplicate Email & Username Handling (`src/services/user_service.py`)**:
   - `DuplicateEmailError` / `UserAlreadyExistsError` raised when email is already registered.
   - `DuplicateUsernameError` / `UsernameAlreadyExistsError` raised when username is already taken.
   - Database level `IntegrityError` rollback handling to catch concurrency race conditions.
   - Profile update duplicate checks ensuring users cannot overwrite someone else's email or username.

5. **Security Utilities (`src/core/security.py`)**:
   - `get_password_hash()` and `verify_password()`.
   - `create_access_token()` and `decode_access_token()`.

6. **M3 Database Integration**:
   - Imported `Base` from `src.core.database`.
   - Exported `User` in `src.models.__init__.py`.
   - Configured Alembic `env.py` to target `Base.metadata` with `User` imported.
   - Created initial migration script `alembic/versions/001_create_users_table.py`.

7. **Automated Unit Testing**:
   - 31 test cases in `tests/test_user_schemas.py`, `tests/test_user_model.py`, and `tests/test_user_service.py`.
   - 100% test pass rate.
