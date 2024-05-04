from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from accounts import models
from accounts.managers import UserManager
from accounts.tests import TEST_EMAIL, TEST_PASSWORD


class UserModelTest(TestCase):
    def setUp(self) -> None:
        self.model_class = models.User
        self.data = {
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        }

    def test_model_inherit_necessary_mixins(self):
        mixins = [PermissionsMixin, AbstractBaseUser]
        [self.assertTrue(issubclass(self.model_class, mixin)) for mixin in mixins]

    def test_email_field_is_required(self):
        with self.assertRaises(ValidationError):
            user = self.model_class.objects.create(password=self.data['password'])
            user.full_clean()

    def test_email_field_is_unique(self):
        self.model_class.objects.create(**self.data)

        self.assertRaisesRegexp(
            IntegrityError,
            r'UNIQUE .+',
            self.model_class.objects.create,
            **self.data,
        )

    def test_email_field_is_username_field(self):
        self.assertEqual(self.model_class.USERNAME_FIELD, 'email')

    def test_email_field_is_email_field(self):
        self.assertEqual(self.model_class.EMAIL_FIELD, 'email')

    def test_is_stuff_field_is_false_by_default(self):
        user = self.model_class.objects.create(**self.data)

        self.assertFalse(user.is_staff)

    def test_model_str_representation_is_email(self):
        user = self.model_class(**self.data)

        self.assertEqual(str(user), self.data['email'])

    def test_model_objects_is_UserManager(self):
        self.assertIsInstance(self.model_class.objects, UserManager)
