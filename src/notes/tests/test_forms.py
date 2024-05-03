from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.test import TestCase
from django import forms as dj_forms

from notes import forms, models

User = get_user_model()


class NoteUpdateForm(TestCase):
    def setUp(self) -> None:
        self.form_class = forms.NoteUpdateForm
        self.user = User.objects.create_user(email='samurai@test.com', password='qwe123!@#')
        self.worktable = models.Worktable.objects.create(user=self.user)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Danger!', color='#ff0000')
        self.note = models.Note.objects.create(
            worktable=self.worktable,
            category=self.category,
            title='OMG! How to understand a woman?',
            text='1001 way to understand a women...',
        )
        self.data = {
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

    def test_form_inherit_ModelForm(self):
        self.assertTrue(issubclass(self.form_class, dj_forms.ModelForm))

    def test_form_updates_note_correctly(self):
        form = self.form_class(instance=self.note, data=self.data)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(self.note.title, self.data['title'])
        self.assertEqual(self.note.text, self.data['text'])


class NoteCreateForm(TestCase):
    def setUp(self) -> None:
        self.form_class = forms.NoteCreateForm
        self.user = User.objects.create_user(email='samurai@test.com', password='qwe123!@#')
        self.worktable = models.Worktable.objects.create(user=self.user)
        self.request = HttpRequest()
        self.request.user = self.user

        self.title = 'Why do flat Earth believers are exist such many?'
        self.data = {
            'category': '',
            'title': self.title,
            'text': '',
        }

    def test_form_inherit_BaseCreateForm(self):
        self.assertTrue(issubclass(self.form_class, forms.BaseCreateForm))

    def test_form_creates_note_correctly(self):
        form = self.form_class(request=self.request, data=self.data)
        self.assertTrue(form.is_valid())

        note = form.save()

        self.assertEqual(note.pk, self.worktable.pk)


class CategoryUpdateForm(TestCase):
    def setUp(self) -> None:
        self.form_class = forms.CategoryUpdateForm
        self.user = User.objects.create_user(email='samurai@test.com', password='qwe123!@#')
        self.worktable = models.Worktable.objects.create(user=self.user)
        self.category = models.Category.objects.create(worktable=self.worktable, title='Screeps World')
        self.data = {
            'title': 'Screeps World +4 CPU',
            'color': '#202020',
        }

    def test_form_inherit_ModelForm(self):
        self.assertTrue(issubclass(self.form_class, dj_forms.ModelForm))

    def test_form_updates_category_correctly(self):
        form = self.form_class(instance=self.category, data=self.data)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(self.category.title, self.data['title'])
        self.assertEqual(self.category.color, self.data['color'])


class CategoryCreateForm(TestCase):
    def setUp(self) -> None:
        self.form_class = forms.CategoryCreateForm
        self.user = User.objects.create_user(email='samurai@test.com', password='qwe123!@#')
        self.worktable = models.Worktable.objects.create(user=self.user)
        self.request = HttpRequest()
        self.request.user = self.user

        self.title = 'Jython'
        self.color = '#202020'
        self.data = {
            'title': self.title,
            'color': self.color,
        }

    def test_form_inherit_BaseCreateForm(self):
        self.assertTrue(issubclass(self.form_class, forms.BaseCreateForm))

    def test_form_creates_category_correctly(self):
        form = self.form_class(request=self.request, data=self.data)
        self.assertTrue(form.is_valid())

        category = form.save()

        self.assertEqual(category.pk, self.worktable.pk)


class BaseCreateFormTest(TestCase):
    def setUp(self) -> None:
        self.form_class = self.get_test_from_class()
        self.request = HttpRequest()
        self.request.user = AnonymousUser()

        self.user = User.objects.create_user(email='samurai@test.com', password='qwe123!@#')
        self.session_key = self.client.session.session_key

    @staticmethod
    def get_test_from_class():
        class TestForm(forms.BaseCreateForm):
            class Meta:
                model = models.Category
                fields = ('title',)

        return TestForm

    def test_form_inherit_ModelForm(self):
        self.assertTrue(issubclass(self.form_class, dj_forms.ModelForm))

    def test_form_set_worktable_by_user(self):
        self.request.user = self.user
        worktable = models.Worktable.objects.create(user=self.user)
        form = self.form_class(request=self.request, data={'title': 'Cython'})
        form.is_valid()
        category = form.save()
        worktable_category = worktable.category_set.first()

        self.assertEqual(category.pk, worktable_category.pk)

    def test_form_set_worktable_by_session(self):
        self.request.session = self.client.session
        worktable = models.Worktable.objects.create(session_key=self.session_key)
        form = self.form_class(request=self.request, data={'title': 'Brython'})
        form.is_valid()
        category = form.save()
        worktable_category = worktable.category_set.first()

        self.assertEqual(category.pk, worktable_category.pk)
