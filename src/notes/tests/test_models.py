from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from notes import models

User = get_user_model()


class WorktableModelTest(TestCase):
    def setUp(self) -> None:
        self.model_class = models.Worktable
        self.user = User.objects.create_user(email='grinch@test.com', password='qwe123!@#')
        self.session = Session.objects.create(expire_date=timezone.now() + timedelta(days=1))
        self.data = {
            'user': self.user,
            'session': self.session,
        }

    def test_user_field_isnt_required(self):
        worktable = self.model_class.objects.create(session=self.session)
        worktable.full_clean()

    def test_session_field_isnt_required(self):
        worktable = self.model_class.objects.create(user=self.user)
        worktable.full_clean()

    def test_model_isnt_created_if_session_or_user_fields_are_empty(self):
        with self.assertRaises(ValidationError):
            worktable = self.model_class.objects.create()
            worktable.full_clean()

    def test_model_isnt_created_if_session_and_user_fields_are_set(self):
        with self.assertRaises(ValidationError):
            worktable = self.model_class.objects.create(**self.data)
            worktable.full_clean()

    def test_model_is_deleted_if_user_was_deleted(self):
        self.assertEqual(self.model_class.objects.count(), 0)

        self.model_class.objects.create(user=self.user)

        self.assertEqual(self.model_class.objects.count(), 1)

        self.user.delete()

        self.assertEqual(self.model_class.objects.count(), 0)

    def test_model_has_one_to_one_relation_with_user(self):
        self.model_class.objects.create(user=self.user)
        self.assertRaisesRegex(
            IntegrityError,
            r'UNIQUE .+',
            self.model_class.objects.create,
            user=self.user,
        )

    def test_model_is_deleted_if_session_was_deleted(self):
        self.assertEqual(self.model_class.objects.count(), 0)

        self.model_class.objects.create(session=self.session)

        self.assertEqual(self.model_class.objects.count(), 1)

        self.session.delete()

        self.assertEqual(self.model_class.objects.count(), 0)

    def test_model_has_one_to_one_relation_with_session(self):
        self.model_class.objects.create(session=self.session)
        self.assertRaisesRegex(
            IntegrityError,
            r'UNIQUE .+',
            self.model_class.objects.create,
            session=self.session,
        )

    def test_model_str_representation_is_user_email_or_session_key(self):
        worktable = self.model_class.objects.create(user=self.user)
        self.assertEqual(str(worktable), self.user.email)

        worktable = self.model_class.objects.create(session=self.session)
        self.assertEqual(str(worktable), str(self.session.session_key))
