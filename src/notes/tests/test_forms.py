from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.http import HttpRequest
from django.test import TestCase
from django import forms as dj_forms
from django.utils import timezone

from notes import forms, models

User = get_user_model()


class BaseCreateFormTest(TestCase):
    def setUp(self) -> None:
        self.form_class = self.get_test_from_class()
        self.request = HttpRequest()
        self.request.user = AnonymousUser()

        self.user = User.objects.create_user(email='samurai@test.com', password='qwe123!@#')
        self.session = Session.objects.create(expire_date=timezone.now() + timedelta(days=1))

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
        self.request.session = self.session
        worktable = models.Worktable.objects.create(session=self.session)
        form = self.form_class(request=self.request, data={'title': 'Brython'})
        form.is_valid()
        category = form.save()
        worktable_category = worktable.category_set.first()

        self.assertEqual(category.pk, worktable_category.pk)
