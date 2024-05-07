from django.contrib.sessions.models import Session
from django.test import TestCase

from django.urls import reverse
from django.utils import timezone
from django.views import generic

from accounts import forms as acc_forms
from notes import views, forms, models, filters, services


class FilterNotesViewTest(TestCase):
    def setUp(self) -> None:
        self.url = reverse('filter_notes')

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

    def test_view_filters_notes_correctly(self):
        expected_data = services.serialize_filter_qs(models.Note.objects.filter(is_archived=False))
        response = self.client.get(self.url, data={'status': filters.NoteFilters.Status.ACTIVE})
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertListEqual(data, expected_data)


class RetrieveCategoryView(TestCase):
    def setUp(self) -> None:
        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Category #1')

        self.url = reverse('retrieve_category', args=[self.category.id])

        self.expected_data = {
            'urls': {'update': reverse('update_category', args=[self.category.id])},
            'category': {
                'id': self.category.id,
                'title': self.category.title,
                'color': self.category.color,
            },
        }

    def test_view_retrieves_category_correctly(self):
        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, self.expected_data)

    def test_view_returns_error_data_if_category_doesnt_exist(self):
        non_existent_id = 999_999_999
        url = reverse('retrieve_category', args=[non_existent_id])

        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertRegex(data['errors'][0], rf'Not found such category by id={non_existent_id}')


class DeleteCategoryView(TestCase):
    def setUp(self) -> None:
        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Category #1')

        self.url = reverse('delete_category', args=[self.category.id])

        self.expected_data = {'category': {'id': self.category.id}}

    def test_view_deletes_category_correctly(self):
        self.assertEqual(models.Category.objects.count(), 1)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Category.objects.count(), 0)

    def test_view_returns_expected_data(self):
        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(data, self.expected_data)

    def test_view_returns_error_data_if_category_doesnt_exist(self):
        non_existent_id = 999_999_999
        url = reverse('delete_category', args=[non_existent_id])

        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertRegex(data['errors'][0], rf'Not found such category by id={non_existent_id}')


class UpdateCategoryView(TestCase):
    def setUp(self) -> None:
        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Category #1')

        self.url = reverse('update_category', args=[self.category.id])

        self.data = {
            'title': 'New Category Title',
            'color': '#FF00FF',
        }

        self.expected_data = {
            'category': {
                'id': self.category.id,
                'title': self.data['title'],
                'color': self.data['color'],
            }
        }

    def test_view_updates_category_correctly(self):
        response = self.client.post(self.url, self.data)
        self.category.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.category.title, self.data['title'])
        self.assertEqual(self.category.color, self.data['color'])

    def test_view_returns_expected_data(self):
        response = self.client.post(self.url, self.data)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(data, self.expected_data)

    def test_returns_error_data_if_form_is_invalid(self):
        response = self.client.post(self.url, {})
        data = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertTrue(data['errors'])

    def test_view_returns_error_if_category_doesnt_exist(self):
        non_existent_id = 999_999_999
        url = reverse('update_category', args=[non_existent_id])

        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertRegex(data['errors'][0], rf'Not found such category by id={non_existent_id}')


class CreateCategoryView(TestCase):
    def setUp(self) -> None:
        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)

        self.url = reverse('create_category')

        self.data = {'title': 'Category #1', 'color': '#FF0000'}

    def test_view_creates_category_correctly(self):
        self.assertEqual(models.Category.objects.count(), 0)

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.Category.objects.count(), 1)

        category = models.Category.objects.first()

        self.assertEqual(category.title, self.data['title'])
        self.assertEqual(category.color, self.data['color'])

    def test_view_returns_expected_data(self):
        response = self.client.post(self.url, self.data)
        data = response.json()
        category = models.Category.objects.first()
        expected_data = {
            'urls': {
                'update': reverse('update_category', args=[category.id]),
                'retrieve': reverse('retrieve_category', args=[category.id]),
                'delete': reverse('delete_category', args=[category.id]),
            },
            'category': {
                'id': category.id,
                'title': category.title,
                'color': category.color,
            },
        }

        self.assertDictEqual(data, expected_data)

    def test_view_returns_error_data(self):
        response = self.client.post(self.url, {})
        data = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertTrue(data.get('errors'))


class DeleteNoteView(TestCase):
    def setUp(self) -> None:
        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.note = models.Note.objects.create(
            worktable=self.worktable,
            title='Note #1',
        )

        self.url = reverse('delete_note', args=[self.note.id])

        self.expected_data = {'note': {'id': self.note.id}}

    def test_view_deletes_note_correctly(self):
        self.assertEqual(models.Note.objects.count(), 1)

        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Note.objects.count(), 0)
        self.assertDictEqual(data, self.expected_data)

    def test_view_returns_error_data_if_note_doesnt_exist(self):
        non_existent_id = 999_999_999
        url = reverse('delete_note', args=[non_existent_id])

        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertRegex(data['errors'][0], rf'Not found such note by id={non_existent_id}')


class ArchiveNoteView(TestCase):
    def setUp(self) -> None:
        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.note = models.Note.objects.create(
            worktable=self.worktable,
            title='Note #1',
        )

        self.url = reverse('archive_note', args=[self.note.id])

        self.expected_data = {'note': {'id': self.note.id}}

    def test_view_archives_note_correctly(self):
        response = self.client.get(self.url)
        data = response.json()
        self.note.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.note.is_archived)
        self.assertDictEqual(data, self.expected_data)

    def test_view_unarchives_note_if_it_was_archived(self):
        self.note.is_archived = True
        self.note.save()

        response = self.client.get(self.url)
        data = response.json()
        self.note.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.note.is_archived)
        self.assertDictEqual(data, self.expected_data)

    def test_view_returns_error_data_if_note_doesnt_exist(self):
        non_existent_id = 999_999_999
        url = reverse('archive_note', args=[non_existent_id])

        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertRegex(data['errors'][0], rf'Not found such note by id={non_existent_id}')


class RetrieveNoteView(TestCase):
    def setUp(self) -> None:
        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Category #1')
        self.note = models.Note.objects.create(
            worktable=self.worktable,
            title='Note #1',
            text='Some Text',
            category=self.category,
        )

        self.url = reverse('retrieve_note', args=[self.note.id])

        self.expected_date = {
            'urls': {'update': reverse('update_note', args=[self.note.id])},
            'note': {'title': self.note.title, 'text': self.note.text},
            'category': {
                'id': self.category.id,
                'title': self.category.title,
                'color': self.category.color,
            },
        }

    def test_view_returns_data_with_category(self):
        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(data, self.expected_date)

    def test_view_returns_data_without_category(self):
        self.note.category = None
        self.note.save()
        del self.expected_date['category']

        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(data, self.expected_date)

    def test_view_returns_error_data_if_note_doesnt_exist(self):
        non_existent_id = 999_999_999
        url = reverse('retrieve_note', args=[non_existent_id])

        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertRegex(data['errors'][0], rf'Not found such note by id={non_existent_id}')


class UpdateNoteView(TestCase):
    def setUp(self) -> None:
        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Category #1')
        self.note = models.Note.objects.create(worktable=self.worktable, title='Note #1')

        self.url = reverse('update_note', args=[self.note.id])

        self.data = {'category': self.category.id, 'title': 'Note #2', 'text': 'Some Text'}
        self.expected_date = {
            'note': {
                'id': self.note.id,
                'title': self.data['title'],
            },
            'category': {
                'title': self.category.title,
                'color': self.category.color,
            },
        }

    def test_view_updates_note_correctly(self):
        response = self.client.post(self.url, self.data)
        self.note.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.note.category.id, self.data['category'])
        self.assertEqual(self.note.title, self.data['title'])
        self.assertEqual(self.note.text, self.data['text'])

    def test_view_returns_data_with_category(self):
        response = self.client.post(self.url, self.data)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(data, self.expected_date)

    def test_view_returns_data_without_category(self):
        del self.data['category']
        del self.expected_date['category']

        response = self.client.post(self.url, self.data)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(data, self.expected_date)

    def test_view_returns_error_data(self):
        response = self.client.post(self.url, {})
        data = response.json()
        errors = data.get('errors')

        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(errors)
        self.assertTrue(errors, msg='Data is empty.')


class CreateNewNoteView(TestCase):
    def setUp(self) -> None:
        self.url = reverse('create_note')

        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Category #1')

        self.data = {'category': self.category.id, 'title': 'Note #1', 'text': 'Some text'}

        self.expected_data = {
            'note': {
                'title': self.data['title'],
                'date': timezone.now().strftime('%d.%m.%Y'),
            },
            'category': {
                'title': self.category.title,
                'color': self.category.color,
            },
        }

    def add_urls_to_expected_data(self, id):
        self.expected_data['urls'] = {
            'update': reverse('update_note', args=[id]),
            'retrieve': reverse('retrieve_note', args=[id]),
            'archive': reverse('archive_note', args=[id]),
            'delete': reverse('delete_note', args=[id]),
        }

    def test_view_creates_note_correctly(self):
        self.assertEqual(models.Note.objects.count(), 0)

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.Note.objects.count(), 1)

        note = models.Note.objects.first()

        self.assertEqual(note.category.pk, self.category.pk)
        self.assertEqual(note.title, self.data['title'])
        self.assertEqual(note.text, self.data['text'])

    def test_view_returns_expected_data_with_category(self):
        response = self.client.post(self.url, self.data)
        data = response.json()
        note = models.Note.objects.first()
        self.add_urls_to_expected_data(note.id)
        self.expected_data['note']['id'] = note.id

        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(data, self.expected_data)

    def test_view_returns_expected_data_without_category(self):
        del self.data['category']
        del self.expected_data['category']

        response = self.client.post(self.url, self.data)
        data = response.json()
        note = models.Note.objects.first()
        self.add_urls_to_expected_data(note.id)
        self.expected_data['note']['id'] = note.id

        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(data, self.expected_data)

    def test_view_returns_error_data(self):
        response = self.client.post(self.url, {})
        data = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertTrue(data.get('errors'))


class BaseViewTest(TestCase):
    def setUp(self) -> None:
        self.url = reverse('__base_view')
        self.view_class = views.BaseView

    def test_view_inherit_expected_mixins(self):
        mixins = [generic.base.TemplateResponseMixin, generic.base.ContextMixin]
        for mixin in mixins:
            self.assertTrue(issubclass(self.view_class, mixin))

    def test_view_context_has_expected_forms(self):
        expected_forms = {
            'login_form': acc_forms.UserLoginForm,
            'register_form': acc_forms.UserRegisterForm,
        }
        response = self.client.get(self.url)

        for key, cls in expected_forms.items():
            if (form := response.context.get(key)) is not None:
                self.assertIsInstance(form, cls)
            else:
                self.fail(f'Missed <{cls.__name__}>.')

    def test_view_context_has_worktable(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context.get('worktable'), models.Worktable)

    def test_view_creates_session_if_session_key_is_none(self):
        self.assertEqual(Session.objects.count(), 0)

        self.client.get(self.url)

        self.assertEqual(Session.objects.count(), 1)

    def test_view_creates_worktable_if_session_doesnt_have_it(self):
        self.assertEqual(models.Worktable.objects.count(), 0)

        response = self.client.get(self.url)

        self.assertEqual(models.Worktable.objects.count(), 1)

        worktable = response.context.get('worktable')

        self.assertIsInstance(worktable, models.Worktable)
        self.assertEqual(worktable.session_key, self.client.session.session_key)


class NotesViewTest(TestCase):
    def setUp(self) -> None:
        self.url = reverse('home')

    def test_view_uses_expected_template(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'home.html')

    def test_view_context_has_expected_forms(self):
        expected_forms = {
            'note_create_form': forms.NoteCreateForm,
            'filter_form': forms.NoteFiltersForm,
        }
        response = self.client.get(self.url)

        for key, cls in expected_forms.items():
            if (form := response.context.get(key)) is not None:
                self.assertIsInstance(form, cls)
            else:
                self.fail(f'Missed <{cls.__name__}>.')


class CategoriesViewTest(TestCase):
    def setUp(self) -> None:
        self.url = reverse('categories')

    def test_view_uses_expected_template(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'categories.html')

    def test_view_context_has_expected_forms(self):
        expected_forms = {
            'category_create_form': forms.CategoryCreateForm,
        }
        response = self.client.get(self.url)

        for key, cls in expected_forms.items():
            if (form := response.context.get(key)) is not None:
                self.assertIsInstance(form, cls)
            else:
                self.fail(f'Missed <{cls.__name__}>.')
