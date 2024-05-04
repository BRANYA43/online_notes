from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from accounts.tests import TEST_EMAIL, TEST_PASSWORD
from notes import models

User = get_user_model()


class NoteModelTest(TestCase):
    def setUp(self) -> None:
        self.model_class = models.Note

        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Fruit')

        self.data = {
            'worktable': self.worktable,
            'title': 'How do I get mass before summer?',
        }

    def test_worktable_field_is_required(self):
        del self.data['worktable']
        with self.assertRaisesRegex(IntegrityError, r'NOT NULL .+'):
            note = self.model_class.objects.create(**self.data)
            note.full_clean()

    def test_category_field_isnt_required(self):
        note = self.model_class.objects.create(**self.data)
        note.full_clean()  # not raise error

    def test_title_field_is_required(self):
        del self.data['title']
        with self.assertRaisesRegex(ValidationError, r'.+title.+This field cannot be blank.+'):
            note = self.model_class.objects.create(**self.data)
            note.full_clean()

    def test_text_field_isnt_required(self):
        note = self.model_class.objects.create(**self.data)
        note.full_clean()  # not raise error

    def test_is_archived_field_is_false_by_default(self):
        note = self.model_class.objects.create(**self.data)
        note.full_clean()

        self.assertFalse(note.is_archived)

    def test_created_field_is_set_automatically(self):
        note = self.model_class.objects.create(**self.data)
        note.full_clean()

        self.assertAlmostEquals(note.created, timezone.now(), delta=timedelta(seconds=1))

    def test_model_has_many_to_one_relation_with_worktable(self):
        self.model_class.objects.create(**self.data)
        self.model_class.objects.create(**self.data)  # not raise

    def test_model_is_deleted_if_worktable_was_deleted(self):
        self.assertEqual(self.model_class.objects.count(), 0)

        self.model_class.objects.create(**self.data)

        self.assertEqual(self.model_class.objects.count(), 1)

        self.worktable.delete()

        self.assertEqual(self.model_class.objects.count(), 0)

    def test_model_has_many_to_one_relation_with_category(self):
        self.data['category'] = self.category
        self.model_class.objects.create(**self.data)
        self.model_class.objects.create(**self.data)  # not raise error

    def test_category_field_is_set_null_if_category_was_deleted(self):
        self.data['category'] = self.category
        note = self.model_class.objects.create(**self.data)

        self.assertEqual(note.category.pk, self.category.pk)

        self.category.delete()
        note.refresh_from_db()

        self.assertIsNone(note.category)

    def test_model_str_representation_is_title(self):
        note = self.model_class(**self.data)
        self.assertEqual(str(note), self.data['title'])


class CategoryModelTest(TestCase):
    def setUp(self) -> None:
        self.model_class = models.Category

        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)

        self.data = {
            'worktable': self.worktable,
            'title': 'Anime',
        }

    def test_worktable_field_is_required(self):
        del self.data['worktable']
        with self.assertRaisesRegex(IntegrityError, r'NOT NULL .+'):
            category = self.model_class.objects.create(**self.data)
            category.full_clean()

    def test_title_field_is_required(self):
        del self.data['title']
        with self.assertRaisesRegex(ValidationError, r'.+title.+This field cannot be blank.+'):
            category = self.model_class.objects.create(**self.data)
            category.full_clean()

    def test_color_field_is_white_by_default(self):
        category = self.model_class.objects.create(**self.data)
        self.assertEqual(category.color, '#FFFFFF')

    def test_model_has_many_to_one_relation_with_worktable(self):
        self.model_class.objects.create(**self.data)
        self.model_class.objects.create(**self.data)  # not raise error

    def test_model_is_deleted_if_worktable_was_deleted(self):
        self.assertEqual(self.model_class.objects.count(), 0)

        self.model_class.objects.create(**self.data)

        self.assertEqual(self.model_class.objects.count(), 1)

        self.worktable.delete()

        self.assertEqual(self.model_class.objects.count(), 0)

    def test_model_str_representation_is_title(self):
        category = self.model_class.objects.create(**self.data)

        self.assertEqual(str(category), category.title)


class WorktableModelTest(TestCase):
    def setUp(self) -> None:
        self.model_class = models.Worktable

        self.user = User.objects.create_user(email=TEST_EMAIL, password=TEST_PASSWORD)
        self.client.session.save()
        self.session_key = self.client.session.session_key

    def test_user_field_isnt_required(self):
        worktable = self.model_class.objects.create(session_key=self.session_key)
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
            worktable = self.model_class.objects.create(session_key=self.session_key, user=self.user)
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

        self.model_class.objects.create(session_key=self.session_key)

        self.assertEqual(self.model_class.objects.count(), 1)

        Session.objects.get(session_key=self.session_key).delete()

        self.assertEqual(self.model_class.objects.count(), 0)

    def test_model_has_one_to_one_relation_with_session(self):
        self.model_class.objects.create(session_key=self.session_key)

        with self.assertRaisesRegex(ValidationError, r'.+Worktable with this Session already exists.+'):
            worktable = self.model_class.objects.create(session_key=self.session_key)
            worktable.full_clean()

    def test_model_str_representation_is_user_email_or_session_key(self):
        worktable = self.model_class.objects.create(user=self.user)
        self.assertEqual(str(worktable), self.user.email)

        worktable = self.model_class.objects.create(session_key=self.session_key)
        self.assertEqual(str(worktable), self.session_key)

    def test_get_all_categories_method_returns_all_worktable_categories(self):
        category_titles = ('#1', '#2', '#3')
        worktable = self.model_class.objects.create(user=self.user)
        models.Category.objects.bulk_create(
            [models.Category(worktable=worktable, title=title) for title in category_titles]
        )

        for category, expected_title in zip(worktable.get_all_categories(), category_titles):
            self.assertEqual(category.title, expected_title)

    def test_get_all_active_notes_method_returns_only_all_worktable_active_notes(self):
        notes_titles = ('#1', '#2', '#3')
        worktable = self.model_class.objects.create(user=self.user)
        models.Note.objects.bulk_create([models.Note(worktable=worktable, title=title) for title in notes_titles])

        for note, expected_title in zip(worktable.get_all_active_notes().order_by('title'), notes_titles):
            self.assertEqual(note.title, expected_title)

    def test_get_all_archived_notes_method_returns_only_all_worktable_active_notes(self):
        notes_titles = ('#1', '#2', '#3')
        worktable = self.model_class.objects.create(user=self.user)
        models.Note.objects.bulk_create(
            [models.Note(worktable=worktable, title=title, is_archived=True) for title in notes_titles],
        )

        for note, expected_title in zip(worktable.get_all_active_notes().order_by('title'), notes_titles):
            self.assertEqual(note.title, expected_title)
