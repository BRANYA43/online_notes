from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from accounts import models
from accounts.managers import UserManager


class UserModelTest(TestCase):
    def setUp(self) -> None:
        self.model_class = models.User
        self.email = 'rick.sanchez@test.com'
        self.password = 'qwe123!@#'
        self.data = {
            'email': self.email,
            'password': self.password,
        }

    def test_model_inherit_necessary_mixins(self):
        mixins = [PermissionsMixin, AbstractBaseUser]
        [self.assertTrue(issubclass(self.model_class, mixin)) for mixin in mixins]

    def test_email_field_is_required(self):
        with self.assertRaises(ValidationError):
            user = self.model_class.objects.create(password=self.password)
            user.full_clean()

    def test_email_field_is_unique(self):
        self.model_class.objects.create(**self.data)
        self.assertRaises(IntegrityError, self.model_class.objects.create, **self.data)

    def test_email_field_is_username_field(self):
        self.assertEqual(self.model_class.USERNAME_FIELD, 'email')

    def test_email_field_is_email_field(self):
        self.assertEqual(self.model_class.EMAIL_FIELD, 'email')

    def test_model_str_representation_is_email(self):
        user = self.model_class(**self.data)
        self.assertEqual(str(user), self.email)

    def test_model_objects_is_UserManager(self):
        self.assertIsInstance(self.model_class.objects, UserManager)
