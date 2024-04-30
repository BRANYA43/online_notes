from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.test import TestCase

from accounts import managers


class UserManagerTest(TestCase):
    def setUp(self) -> None:
        self.manager = managers.UserManager()
        self.manager.model = get_user_model()
        self.email = 'levi.akerman@test.com'
        self.password = 'qwe123!@#'
        self.data = {
            'email': self.email,
            'password': self.password,
        }

    def test_manager_inherit_BaseUserManager(self):
        self.assertTrue(issubclass(type(self.manager), BaseUserManager))

    def test_manager_creates_user_correctly(self):
        user = self.manager.create_user(**self.data)

        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))
        self.assertFalse(user.is_superuser)

    def test_manager_creates_superuser_correctly(self):
        user = self.manager.create_superuser(**self.data)

        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)