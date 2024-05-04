from django.test import TestCase

from django.urls import reverse
from django.utils import timezone
from django.views import generic

from accounts import forms as acc_forms
from notes import views, forms, models


class CreateNewNoteView(TestCase):
    def setUp(self) -> None:
        self.url = reverse('create_note')
        self.client.session.save()
        self.worktable = models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Category #1')
        self.title = 'Note #1'
        self.text = 'Some text'

        self.data = {
            'category': self.category.id,
            'title': self.title,
            'text': self.text,
        }

        self.expected_data = {
            'note': {'title': self.title, 'date': timezone.now().strftime('%d.%m.%Y')},
            'category': {'title': self.category.title, 'color': self.category.color},
        }

    def test_view_creates_note_correctly(self):
        self.assertEqual(models.Note.objects.count(), 0)

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.Note.objects.count(), 1)

        note = models.Note.objects.first()

        self.assertEqual(note.category.pk, self.category.pk)
        self.assertEqual(note.title, self.title)
        self.assertEqual(note.text, self.text)

    def test_view_returns_expected_data_with_category(self):
        response = self.client.post(self.url, self.data)
        data = response.json()
        note = models.Note.objects.first()
        self.expected_data['url'] = reverse('update_note', args=[note.id])

        self.assertDictEqual(data, self.expected_data)

    def test_view_returns_expected_data_without_category(self):
        del self.data['category']
        del self.expected_data['category']

        response = self.client.post(self.url, self.data)
        note = models.Note.objects.first()
        self.expected_data['url'] = reverse('update_note', args=[note.id])
        data = response.json()

        self.assertDictEqual(data, self.expected_data)

    def test_view_returns_error_data(self):
        response = self.client.post(self.url, {})
        data = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertTrue(data.get('errors'))


class HomeViewTest(TestCase):
    def setUp(self) -> None:
        self.url = reverse('home')
        self.view_class = views.HomeView
        self.client.session.save()

    def test_view_inherit_expected_mixins(self):
        mixins = [generic.base.TemplateResponseMixin, generic.base.ContextMixin]
        for mixin in mixins:
            self.assertTrue(issubclass(self.view_class, mixin))

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'home.html')

    def test_view_context_has_expected_forms(self):
        expected_forms = {
            'login_form': acc_forms.UserLoginForm,
            'register_form': acc_forms.UserRegisterForm,
            'category_create_form': forms.CategoryCreateForm,
            'note_create_form': forms.NoteCreateForm,
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

    def test_view_creates_worktable_if_session_doesnt_have_it(self):
        self.assertEqual(models.Worktable.objects.count(), 0)

        response = self.client.get(self.url)

        self.assertEqual(models.Worktable.objects.count(), 1)

        worktable = response.context.get('worktable')

        self.assertIsInstance(worktable, models.Worktable)
        self.assertEqual(worktable.session_key, self.client.session.session_key)
