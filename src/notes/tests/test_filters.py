from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from notes import models, filters


class NoteFilterTest(TestCase):
    def setUp(self) -> None:
        self.filter_class = filters.NoteFilter
        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Category #1')
        models.Note.objects.bulk_create(
            [
                models.Note(
                    worktable=self.worktable,
                    title=f'Note #{n}',
                    category=category,
                    words=n * 10,
                    unique_words=n,
                    is_archived=True if n == 3 else False,
                )
                for n, category in enumerate((self.category, self.category, None), start=1)
            ]
        )

    def test_filter_filters_notes_by_category(self):
        expected_qs = models.Note.objects.filter(category=self.category)
        filter_ = self.filter_class(data={'category': self.category.id})

        self.assertEqual(filter_.qs.count(), 2)
        self.assertQuerySetEqual(filter_.qs, expected_qs)

    def test_filter_filters_notes_by_active_status(self):
        expected_qs = models.Note.objects.filter(is_archived=False)
        filter_ = self.filter_class(data={'status': self.filter_class.Status.ACTIVE})

        self.assertEqual(filter_.qs.count(), 2)
        self.assertQuerySetEqual(filter_.qs, expected_qs)

    def test_filter_filters_notes_by_archived_status(self):
        expected_qs = models.Note.objects.filter(is_archived=True)
        filter_ = self.filter_class(data={'status': self.filter_class.Status.ARCHIVED})

        self.assertEqual(filter_.qs.count(), 1)
        self.assertQuerySetEqual(filter_.qs, expected_qs)

    def test_filter_filters_notes_by_quantity_words_range(self):
        expected_qs = models.Note.objects.filter(words__range=(0, 20))
        filter_ = self.filter_class(data={'words_min': '0', 'words_max': '20'})

        self.assertEqual(filter_.qs.count(), 2)
        self.assertQuerySetEqual(filter_.qs, expected_qs)

    def test_filter_filters_notes_by_increasing_quantity_unique_words(self):
        expected_qs = models.Note.objects.filter(unique_words__range=(0, 2))
        filter_ = self.filter_class(data={'unique_words_min': 0, 'unique_words_max': 2})

        self.assertEqual(filter_.qs.count(), 2)
        self.assertQuerySetEqual(filter_.qs, expected_qs)

    def test_filter_filters_notes_by_range_created_date(self):
        note = models.Note.objects.first()
        note.created = timezone.now() + timedelta(days=2)
        note.save()

        start_date = timezone.now() - timedelta(days=1)
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = timezone.now() + timedelta(days=1)
        end_date = end_date.strftime('%Y-%m-%d')

        expected_qs = models.Note.objects.filter(created__range=(start_date, end_date))
        filter_ = self.filter_class(
            data={
                'created_after': start_date,
                'created_before': end_date,
            }
        )

        self.assertEqual(filter_.qs.count(), 2)
        self.assertQuerySetEqual(filter_.qs, expected_qs)
