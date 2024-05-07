from django.contrib.sessions.models import Session
from django.test import TestCase

from notes import models


class SetQuantityOfAllWordsTest(TestCase):
    def setUp(self) -> None:
        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.data = {
            'worktable': self.worktable,
            'title': 'Note #1',
            'text': 'Bananas, bananas, bananas, Pickles',
        }

    def test_signal_set_words_and_unique_words_fields_for_note(self):
        note = models.Note.objects.create(**self.data)
        self.assertEqual(note.words, 4)
        self.assertEqual(note.unique_words, 1)


class DeleteWorktableAfterDeletingSessionSignalTest(TestCase):
    def setUp(self) -> None:
        self.client.session.save()
        self.session = Session.objects.get(session_key=self.client.session.session_key)
        self.worktable = models.Worktable.objects.create(session_key=self.session.session_key)

    def test_signal_deletes_worktable_after_deleting_session(self):
        self.assertEqual(models.Worktable.objects.count(), 1)

        self.session.delete()

        self.assertEqual(models.Worktable.objects.count(), 0)

    def test_signal_doesnt_raise_error_if_worktable_doesnt_exist_with_such_session_key(self):
        self.worktable.delete()

        self.assertEqual(models.Worktable.objects.count(), 0)

        self.session.delete()  # not raise

        self.assertEqual(models.Worktable.objects.count(), 0)
