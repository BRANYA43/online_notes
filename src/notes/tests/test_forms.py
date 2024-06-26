from django.contrib.auth import get_user_model
from django.test import TestCase
from django import forms as dj_forms

from accounts.tests import TEST_EMAIL, TEST_PASSWORD
from notes import forms, models
from notes.tests import get_test_request

User = get_user_model()


class NoteUpdateForm(TestCase):
    def setUp(self) -> None:
        self.form_class = forms.NoteUpdateForm

        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Danger', color='#ff0000')
        self.note = models.Note.objects.create(
            worktable=self.worktable,
            title='OMG! How to understand a woman?',
            text='1001 way to understand a women...',
        )

        self.data = {
            'category': self.category.id,
            'title': 'How to understand a man?',
            'text': 'Man Language:\n'
            'nod down - hi;\n'
            "nod up - what's up;\n"
            "nod to the left - let's step back, we need to talk;\n"
            'nod to the right - come and look at;\n'
            "head forward - what's wrong with you?;\n"
            'head back - what the hell?;\n'
            'all other times - shrug;',
        }

    def test_form_inherits_ModelForm(self):
        self.assertTrue(issubclass(self.form_class, dj_forms.ModelForm))

    def test_form_updates_note_correctly(self):
        self.assertIsNone(self.note.category)
        self.assertNotEqual(self.note.title, self.data['title'])
        self.assertNotEqual(self.note.text, self.data['text'])

        form = self.form_class(instance=self.note, data=self.data)
        self.assertTrue(form.is_valid())
        form.save()
        self.note.refresh_from_db()

        self.assertEqual(self.note.category.id, self.data['category'])
        self.assertEqual(self.note.title, self.data['title'])
        self.assertEqual(self.note.text, self.data['text'])


class NoteCreateForm(TestCase):
    def setUp(self) -> None:
        self.form_class = forms.NoteCreateForm
        self.request = get_test_request(self.client)

        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Category #1', color='#ff0000')

        self.data = {
            'category': self.category.id,
            'title': 'Why do flat Earth believers are exist such many?',
            'text': "I don't know...",
        }

    def test_form_inherits_BaseCreateForm(self):
        self.assertTrue(issubclass(self.form_class, forms.BaseCreateForm))

    def test_form_creates_note_correctly(self):
        self.assertEqual(models.Note.objects.count(), 0)

        form = self.form_class(request=self.request, data=self.data)
        self.assertTrue(form.is_valid())
        note = form.save()

        self.assertEqual(models.Note.objects.count(), 1)
        self.assertTrue(models.Note.objects.filter(id=note.id))
        self.assertEqual(note.worktable.pk, self.worktable.pk)
        self.assertEqual(note.title, self.data['title'])
        self.assertEqual(note.category.id, self.data['category'])
        self.assertEqual(note.text, self.data['text'])

    def test_category_filter_returns_categories_of_current_worktable(self):
        morty_worktable = models.Worktable.objects.create(session_key='morty_worktable_session_key')
        morty_category = models.Category.objects.create(worktable=morty_worktable, title='Morty Note')
        form = self.form_class(request=self.request)
        category_qs = form.fields['category'].queryset

        self.assertQuerySetEqual(category_qs, self.worktable.get_all_categories())
        self.assertFalse(category_qs.filter(id=morty_category.id))


class CategoryUpdateForm(TestCase):
    def setUp(self) -> None:
        self.form_class = forms.CategoryUpdateForm

        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Category #1')

        self.data = {
            'title': 'Category #2',
            'color': '#202020',
        }

    def test_form_inherits_ModelForm(self):
        self.assertTrue(issubclass(self.form_class, dj_forms.ModelForm))

    def test_form_updates_category_correctly(self):
        self.assertNotEqual(self.category.title, self.data['title'])
        self.assertNotEqual(self.category.color, self.data['color'])

        form = self.form_class(instance=self.category, data=self.data)
        self.assertTrue(form.is_valid())
        form.save()
        self.category.refresh_from_db()

        self.assertEqual(self.category.title, self.data['title'])
        self.assertEqual(self.category.color, self.data['color'])


class CategoryCreateForm(TestCase):
    def setUp(self) -> None:
        self.form_class = forms.CategoryCreateForm
        self.request = get_test_request(self.client)

        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)

        self.data = {
            'title': 'Jython',
            'color': '#202020',
        }

    def test_form_inherits_BaseCreateForm(self):
        self.assertTrue(issubclass(self.form_class, forms.BaseCreateForm))

    def test_form_creates_category_correctly(self):
        self.assertEqual(models.Category.objects.count(), 0)

        form = self.form_class(request=self.request, data=self.data)
        self.assertTrue(form.is_valid())
        category = form.save()

        self.assertEqual(models.Category.objects.count(), 1)
        self.assertTrue(models.Category.objects.filter(id=category.id))
        self.assertEqual(category.worktable.pk, self.worktable.pk)
        self.assertEqual(category.title, self.data['title'])
        self.assertEqual(category.color, self.data['color'])


class BaseCreateFormTest(TestCase):
    def setUp(self) -> None:
        self.form_class = self.get_test_from_class()
        self.request = get_test_request(self.client)

        self.user = User.objects.create_user(email=TEST_EMAIL, password=TEST_PASSWORD)

        self.data = {'title': 'Cython'}

    @staticmethod
    def get_test_from_class() -> type:
        return type(
            'TestForm',
            (forms.BaseCreateForm,),
            {'Meta': type('Meta', (), {'model': models.Category, 'fields': ('title',)})},
        )

    def test_form_inherits_ModelForm(self):
        self.assertTrue(issubclass(self.form_class, dj_forms.ModelForm))

    def test_form_sets_worktable_by_user(self):
        self.request.user = self.user
        worktable = models.Worktable.objects.create(user=self.user)

        form = self.form_class(self.request, self.data)
        form.is_valid()
        category = form.save()

        self.assertEqual(category.worktable.pk, worktable.pk)

    def test_form_sets_worktable_by_session(self):
        worktable = models.Worktable.objects.create(session_key=self.request.session.session_key)

        form = self.form_class(self.request, self.data)
        form.is_valid()
        category = form.save()

        self.assertEqual(category.worktable.pk, worktable.pk)
