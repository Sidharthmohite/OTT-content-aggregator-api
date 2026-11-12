"""Unit tests for the User SQLAlchemy database model (M2).
"""

from datetime import datetime, timezone
import unittest

from src.models.user import User


class TestUserModel(unittest.TestCase):
    """Test suite verifying User model definition, attributes, and behavior."""

    def test_table_name(self):
        """Test that the User model table name is 'users'."""
        self.assertEqual(User.__tablename__, "users")

    def test_user_instantiation_and_defaults(self):
        """Test user instance attributes and default values."""
        now = datetime.now(timezone.utc)
        user = User(
            id=1,
            email="testuser@example.com",
            username="testuser",
            hashed_password="hashed_pw_string",
            full_name="Test User",
            is_active=True,
            is_superuser=False,
            created_at=now,
            updated_at=now,
        )
        self.assertEqual(user.id, 1)
        self.assertEqual(user.email, "testuser@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.hashed_password, "hashed_pw_string")
        self.assertEqual(user.full_name, "Test User")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.created_at, now)
        self.assertEqual(user.updated_at, now)

    def test_user_repr(self):
        """Test that __repr__ provides clear human-readable string representation."""
        user = User(
            id=42,
            email="alice@example.com",
            username="alice",
            hashed_password="pw",
            is_active=True,
        )
        repr_str = repr(user)
        self.assertIn("id=42", repr_str)
        self.assertIn("username='alice'", repr_str)
        self.assertIn("email='alice@example.com'", repr_str)
        self.assertIn("is_active=True", repr_str)


if __name__ == "__main__":
    unittest.main()
