"""Unit tests for UserService, authentication, and duplicate email/username handling (M2).
"""

from datetime import datetime, timezone
import unittest

from src.core.security import verify_password
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.services.user_service import (
    DuplicateEmailError,
    DuplicateUsernameError,
    UserNotFoundError,
    UserService,
)


class MockDatabaseSession:
    """In-memory mock session supporting database operations for standalone unit testing."""

    def __init__(self):
        self.users: dict[int, User] = {}
        self._next_id = 1

    def add(self, instance: User):
        if instance.id is None:
            instance.id = self._next_id
            self._next_id += 1
        self.users[instance.id] = instance

    def commit(self):
        pass

    def rollback(self):
        pass

    def refresh(self, instance: User):
        pass

    def get(self, user_id: int) -> User | None:
        return self.users.get(user_id)

    def find_by_email(self, email: str) -> User | None:
        normalized = email.strip().lower()
        for user in self.users.values():
            if user.email.lower() == normalized:
                return user
        return None

    def find_by_username(self, username: str) -> User | None:
        cleaned = username.strip()
        for user in self.users.values():
            if user.username == cleaned:
                return user
        return None


class TestUserService(unittest.TestCase):
    """Test suite for UserService and duplicate email handling."""

    def setUp(self):
        self.db = MockDatabaseSession()
        self.valid_payload = UserCreate(
            email="alice@example.com",
            username="alice_wonderland",
            full_name="Alice Liddell",
            password="StrongPassword123!",
        )

    def test_create_user_successful(self):
        """Test successful user creation with password hashing and email normalization."""
        user = UserService.create_user(self.db, self.valid_payload)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, "alice@example.com")
        self.assertEqual(user.username, "alice_wonderland")
        self.assertNotEqual(user.hashed_password, "StrongPassword123!")
        self.assertTrue(verify_password("StrongPassword123!", user.hashed_password))

    def test_duplicate_email_rejected(self):
        """Test that registering with an already existing email raises DuplicateEmailError."""
        # Create initial user
        UserService.create_user(self.db, self.valid_payload)

        # Attempt to register duplicate email with different username
        duplicate_payload = UserCreate(
            email="alice@example.com",
            username="alice_second_account",
            password="AnotherPassword999!",
        )
        with self.assertRaises(DuplicateEmailError) as ctx:
            UserService.create_user(self.db, duplicate_payload)

        self.assertIn("already registered", str(ctx.exception))

    def test_duplicate_email_case_insensitive_rejected(self):
        """Test that duplicate emails with different casing are caught and rejected."""
        UserService.create_user(self.db, self.valid_payload)

        # Attempt with uppercase variant
        uppercase_payload = UserCreate(
            email="ALICE@EXAMPLE.COM",
            username="alice_different_username",
            password="AnotherPassword999!",
        )
        with self.assertRaises(DuplicateEmailError) as ctx:
            UserService.create_user(self.db, uppercase_payload)

        self.assertIn("already registered", str(ctx.exception))

    def test_duplicate_username_rejected(self):
        """Test that registering with an already existing username raises DuplicateUsernameError."""
        UserService.create_user(self.db, self.valid_payload)

        # Attempt to register same username with different email
        duplicate_username_payload = UserCreate(
            email="different_email@example.com",
            username="alice_wonderland",
            password="AnotherPassword999!",
        )
        with self.assertRaises(DuplicateUsernameError) as ctx:
            UserService.create_user(self.db, duplicate_username_payload)

        self.assertIn("already taken", str(ctx.exception))

    def test_get_user_by_id_and_email_and_username(self):
        """Test user retrieval helpers."""
        created = UserService.create_user(self.db, self.valid_payload)

        by_id = UserService.get_user_by_id(self.db, created.id)
        self.assertEqual(by_id, created)

        by_email = UserService.get_user_by_email(self.db, "alice@example.com")
        self.assertEqual(by_email, created)

        by_username = UserService.get_user_by_username(self.db, "alice_wonderland")
        self.assertEqual(by_username, created)

        # Non-existent queries
        self.assertIsNone(UserService.get_user_by_id(self.db, 9999))
        self.assertIsNone(UserService.get_user_by_email(self.db, "nonexistent@example.com"))
        self.assertIsNone(UserService.get_user_by_username(self.db, "ghost_user"))

    def test_update_user_profile(self):
        """Test partial profile update."""
        user = UserService.create_user(self.db, self.valid_payload)
        update_data = UserUpdate(full_name="Alice Through The Looking Glass")
        updated = UserService.update_user(self.db, user.id, update_data)
        self.assertEqual(updated.full_name, "Alice Through The Looking Glass")

    def test_update_user_email_duplicate_rejected(self):
        """Test that updating an email to an already existing user's email raises DuplicateEmailError."""
        user1 = UserService.create_user(self.db, self.valid_payload)
        user2 = UserService.create_user(
            self.db,
            UserCreate(
                email="bob@example.com",
                username="bob_marley",
                password="BobPassword123!",
            ),
        )

        # Attempt to change bob's email to alice's email
        with self.assertRaises(DuplicateEmailError):
            UserService.update_user(
                self.db, user2.id, UserUpdate(email="alice@example.com")
            )

    def test_update_user_username_duplicate_rejected(self):
        """Test that updating username to an already existing username raises DuplicateUsernameError."""
        user1 = UserService.create_user(self.db, self.valid_payload)
        user2 = UserService.create_user(
            self.db,
            UserCreate(
                email="bob@example.com",
                username="bob_marley",
                password="BobPassword123!",
            ),
        )

        # Attempt to change bob's username to alice's username
        with self.assertRaises(DuplicateUsernameError):
            UserService.update_user(
                self.db, user2.id, UserUpdate(username="alice_wonderland")
            )

    def test_update_nonexistent_user(self):
        """Test that updating a non-existent user raises UserNotFoundError."""
        with self.assertRaises(UserNotFoundError):
            UserService.update_user(self.db, 9999, UserUpdate(full_name="Nobody"))

    def test_authenticate_user_success(self):
        """Test user authentication with both email and username."""
        UserService.create_user(self.db, self.valid_payload)

        # Login via email
        auth1 = UserService.authenticate_user(
            self.db, "alice@example.com", "StrongPassword123!"
        )
        self.assertIsNotNone(auth1)
        self.assertEqual(auth1.username, "alice_wonderland")

        # Login via username
        auth2 = UserService.authenticate_user(
            self.db, "alice_wonderland", "StrongPassword123!"
        )
        self.assertIsNotNone(auth2)
        self.assertEqual(auth2.email, "alice@example.com")

    def test_authenticate_user_invalid_credentials(self):
        """Test authentication failure with incorrect password or unknown user."""
        UserService.create_user(self.db, self.valid_payload)

        # Wrong password
        auth_bad_pw = UserService.authenticate_user(
            self.db, "alice@example.com", "WrongPassword999!"
        )
        self.assertIsNone(auth_bad_pw)

        # Non-existent user
        auth_bad_user = UserService.authenticate_user(
            self.db, "unknown@example.com", "StrongPassword123!"
        )
        self.assertIsNone(auth_bad_user)


if __name__ == "__main__":
    unittest.main()
