"""Unit tests for User Pydantic schemas and field validations (M2).
"""

from datetime import datetime, timezone
import unittest
from pydantic import ValidationError

from src.schemas.user import (
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)


class TestUserSchemas(unittest.TestCase):
    """Test suite covering UserCreate, UserResponse, UserUpdate schemas and field validators."""

    def test_valid_user_create(self):
        """Test creating a valid UserCreate instance."""
        payload = {
            "email": "testuser@example.com",
            "username": "test_user_1",
            "full_name": "Test User",
            "password": "StrongPassword123!",
        }
        user = UserCreate(**payload)
        self.assertEqual(user.email, "testuser@example.com")
        self.assertEqual(user.username, "test_user_1")
        self.assertEqual(user.full_name, "Test User")
        self.assertEqual(user.password, "StrongPassword123!")
        self.assertTrue(user.is_active)

    def test_email_normalization_to_lowercase(self):
        """Test that email addresses are automatically normalized to lowercase."""
        user = UserCreate(
            email="  User.NAME@Example.COM  ",
            username="valid_user",
            password="StrongPassword123!",
        )
        self.assertEqual(user.email, "user.name@example.com")

    def test_invalid_email_missing_at_symbol(self):
        """Test that an email without an @ symbol fails validation."""
        with self.assertRaises(ValidationError) as ctx:
            UserCreate(
                email="plainaddress",
                username="valid_user",
                password="StrongPassword123!",
            )
        self.assertIn("Invalid email address format", str(ctx.exception))

    def test_invalid_email_missing_domain(self):
        """Test that an email missing top-level domain fails validation."""
        with self.assertRaises(ValidationError) as ctx:
            UserCreate(
                email="user@domain",
                username="valid_user",
                password="StrongPassword123!",
            )
        self.assertIn("Invalid email address format", str(ctx.exception))

    def test_invalid_email_with_spaces(self):
        """Test that an email containing internal spaces fails validation."""
        with self.assertRaises(ValidationError) as ctx:
            UserCreate(
                email="user name@example.com",
                username="valid_user",
                password="StrongPassword123!",
            )
        self.assertIn("Invalid email address format", str(ctx.exception))

    def test_username_too_short(self):
        """Test that usernames shorter than 3 characters fail validation."""
        with self.assertRaises(ValidationError) as ctx:
            UserCreate(
                email="user@example.com",
                username="ab",
                password="StrongPassword123!",
            )
        err = str(ctx.exception)
        self.assertTrue("3 characters" in err)

    def test_username_too_long(self):
        """Test that usernames longer than 50 characters fail validation."""
        long_username = "a" * 51
        with self.assertRaises(ValidationError) as ctx:
            UserCreate(
                email="user@example.com",
                username=long_username,
                password="StrongPassword123!",
            )
        err = str(ctx.exception)
        self.assertTrue("50 characters" in err)

    def test_username_invalid_characters(self):
        """Test that usernames with disallowed symbols (spaces, punctuation) fail."""
        with self.assertRaises(ValidationError) as ctx:
            UserCreate(
                email="user@example.com",
                username="john doe!",
                password="StrongPassword123!",
            )
        self.assertIn("Username can only contain alphanumeric", str(ctx.exception))

    def test_username_valid_formats(self):
        """Test valid usernames with letters, digits, underscores, and hyphens."""
        valid_names = ["john_doe", "jane-doe", "user123", "Cool_Dev-99"]
        for name in valid_names:
            u = UserCreate(
                email="user@example.com",
                username=name,
                password="StrongPassword123!",
            )
            self.assertEqual(u.username, name)

    def test_password_too_short(self):
        """Test password less than 8 characters is rejected."""
        with self.assertRaises(ValidationError) as ctx:
            UserCreate(
                email="user@example.com",
                username="validuser",
                password="Pass1!",
            )
        self.assertIn("at least 8 characters", str(ctx.exception))

    def test_password_missing_uppercase(self):
        """Test password lacking uppercase characters is rejected."""
        with self.assertRaises(ValidationError) as ctx:
            UserCreate(
                email="user@example.com",
                username="validuser",
                password="password123!",
            )
        self.assertIn("uppercase letter", str(ctx.exception))

    def test_password_missing_lowercase(self):
        """Test password lacking lowercase characters is rejected."""
        with self.assertRaises(ValidationError) as ctx:
            UserCreate(
                email="user@example.com",
                username="validuser",
                password="PASSWORD123!",
            )
        self.assertIn("lowercase letter", str(ctx.exception))

    def test_password_missing_digit(self):
        """Test password lacking numeric digits is rejected."""
        with self.assertRaises(ValidationError) as ctx:
            UserCreate(
                email="user@example.com",
                username="validuser",
                password="PasswordNoDigit!",
            )
        self.assertIn("digit", str(ctx.exception))

    def test_password_missing_special_character(self):
        """Test password lacking special characters is rejected."""
        with self.assertRaises(ValidationError) as ctx:
            UserCreate(
                email="user@example.com",
                username="validuser",
                password="Password123NoSpecial",
            )
        self.assertIn("special character", str(ctx.exception))

    def test_user_response_serialization_excludes_password(self):
        """Test that UserResponse safely exposes public fields and omits password."""
        now = datetime.now(timezone.utc)
        response_data = {
            "id": 1,
            "email": "alice@example.com",
            "username": "alice",
            "full_name": "Alice Smith",
            "is_active": True,
            "is_superuser": False,
            "created_at": now,
            "updated_at": now,
        }
        res = UserResponse(**response_data)
        serialized = res.model_dump()
        self.assertNotIn("password", serialized)
        self.assertNotIn("hashed_password", serialized)
        self.assertEqual(serialized["id"], 1)
        self.assertEqual(serialized["email"], "alice@example.com")

    def test_user_update_partial_fields(self):
        """Test that UserUpdate allows updating individual fields without requiring all."""
        update1 = UserUpdate(full_name="New Full Name")
        self.assertEqual(update1.full_name, "New Full Name")
        self.assertIsNone(update1.email)
        self.assertIsNone(update1.username)

        update2 = UserUpdate(email="NEW_EMAIL@example.com")
        self.assertEqual(update2.email, "new_email@example.com")

        update3 = UserUpdate(password="NewSecurePass999#")
        self.assertEqual(update3.password, "NewSecurePass999#")

    def test_user_login_schema(self):
        """Test UserLogin schema accepts username or email and password."""
        login = UserLogin(username_or_email="alice@example.com", password="SecretPassword1!")
        self.assertEqual(login.username_or_email, "alice@example.com")
        self.assertEqual(login.password, "SecretPassword1!")


if __name__ == "__main__":
    unittest.main()
