from django.test import TestCase

from django.urls import reverse

from notes import services, models


class SerializeModelTest(TestCase):
    def setUp(self) -> None:
        self.service_fn = services.serialize_model
        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.note = models.Note.objects.create(worktable=self.worktable, title='Note #1')

        self.expected_data = {
            'urls': {
                'update': reverse('update_note', args=[self.note.id]),
                'retrieve': reverse('retrieve_note', args=[self.note.id]),
                'archive': reverse('archive_note', args=[self.note.id]),
                'delete': reverse('delete_note', args=[self.note.id]),
            },
            'note': {
                'id': self.note.id,
                'title': self.note.title,
                'is_archived': self.note.is_archived,
            },
        }

    def test_service_serialize_note_correctly(self):
        data = self.service_fn(
            self.note,
            fields=('id', 'title', 'is_archived'),
            urls=('update', 'retrieve', 'archive', 'delete'),
        )

        self.assertEqual(data, self.expected_data)


class SerializeFilterQS(TestCase):
    def setUp(self) -> None:
        self.service_fn = services.serialize_filter_qs
        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Category #1')
        self.note = models.Note.objects.create(worktable=self.worktable, title='Note #1', category=self.category)

        self.expected_data = [
            {
                'urls': {
                    'update': reverse('update_note', args=[self.note.id]),
                    'retrieve': reverse('retrieve_note', args=[self.note.id]),
                    'archive': reverse('archive_note', args=[self.note.id]),
                    'delete': reverse('delete_note', args=[self.note.id]),
                },
                'note': {
                    'id': self.note.id,
                    'title': self.note.title,
                    'is_archived': self.note.is_archived,
                    'created': self.note.created.strftime('%d.%m.%Y'),
                },
                'category': {
                    'title': self.category.title,
                    'color': self.category.color,
                },
            }
        ]

    def test_service_serializes_filter_qs_correctly_if_note_has_category(self):
        data = self.service_fn(models.Note.objects.all())

        self.assertListEqual(data, self.expected_data)

    def test_service_serializes_filter_qs_correctly_if_note_doesnt_have_category(self):
        self.note.category = None
        self.note.save()
        self.expected_data[0]['category'] = None

        data = self.service_fn(models.Note.objects.all())

        self.assertListEqual(data, self.expected_data)


class CountAllWordsInTextTest(TestCase):
    def setUp(self) -> None:
        self.service_fn = services.count_words_in_text

        self.text = (
            'Why do I want to become a developer? Because I like to create something and check it how it '
            "work in the moment. It's interest how games or apps creation look like from the inside."
        )

    def test_service_counts_word_quantity_in_text_correctly(self):
        result = self.service_fn(self.text)

        self.assertEqual(result, 36)

    def test_service_counts_unique_word_quantity_in_text_correctly(self):
        result = self.service_fn(self.text, unique=True)

        self.assertEqual(result, 23)
