import unittest
from unittest.mock import MagicMock

from auth.models import Admins, Linked_Admin_Data
from argon2 import PasswordHasher


class TestAdminsModel(unittest.TestCase):
    def setUp(self):
        self.db_session = MagicMock()  # Mock the database session
        self.ph = PasswordHasher(salt_len=16)

    def test_hash_password(self):
        admin = Admins(self.db_session, name="Test Admin",
                       email="test@example.com", password="mypassword")

        # Using Argon2 to verify the hashed result for correctness:
        self.assertTrue(self.ph.verify(admin.password, "mypassword"))

    def test_verify_password(self):
        password = "testpassword"
        admin = Admins(self.db_session, name="Test Admin",
                       email="test@example.com", password=password)

        self.assertFalse(admin.verify_password("incorrect_password"))
        self.assertTrue(admin.verify_password(password))

    def test_create_user(self):
        admin = Admins(self.db_session, name="Test Admin",
                       email="test@example.com", password="testpassword")
        admin.additional_data = Linked_Admin_Data()
        admin.create()

        self.db_session.add.assert_called_once_with(
            admin)
        self.db_session.commit.assert_called_once()

    # ... Add more tests for change_password,
    # get_by_id, get_by_email, update, has_type
