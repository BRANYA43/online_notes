from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase

from django.forms import ModelForm

from accounts import forms
from notes import models as n_models

User = get_user_model()


class UserLoginFormTest(TestCase):
    def setUp(self) -> None:
        self.request = HttpRequest()
        self.form_class = forms.UserLoginForm
        self.email = 'shurup.cherikovich@test.com'
        self.password = 'qwe123!@#'
        self.data = {
            'email': self.email,
            'password': self.password,
        }
        self.user = User.objects.create_user(**self.data)

    def test_form_is_invalid_if_email_is_empty(self):
        self.data['email'] = ''
        form = self.form_class(self.request, data=self.data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'email', ['This field is required.'])

    def test_form_is_invalid_if_password_is_empty(self):
        self.data['password'] = ''
        form = self.form_class(self.request, data=self.data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'password', ['This field is required.'])

    def test_form_is_invalid_if_authenticating_returns_none_user(self):
        self.data['email'] = 'the.non.existent.man@test.com'
        form = self.form_class(self.request, data=self.data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, None, ['Please enter a correct email and password. Note: both fields may be case-sensitive.']
        )

    def test_form_caches_user_if_credentials_passed_authenticating(self):
        form = self.form_class(self.request, data=self.data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cache_user.pk, self.user.pk)


class UserRegisterFormTest(TestCase):
    def setUp(self) -> None:
        self.request = HttpRequest()
        self.request.session = self.client.session
        self.worktable = n_models.Worktable.objects.create(session_key=self.client.session.session_key)
        self.form_class = forms.UserRegisterForm
        self.email = 'god.yato@test.com'
        self.password = 'qwe123!@#'
        self.data = {
            'email': self.email,
            'password': self.password,
            'confirming_password': self.password,
        }

    def test_form_inherit_ModelForm(self):
        self.assertTrue(issubclass(self.form_class, ModelForm))

    def test_form_is_invalid_if_confirming_password_and_password_are_match(self):
        self.data['confirming_password'] = 'unmatch_password'
        form = self.form_class(request=self.request, data=self.data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'confirming_password', ["The passwords didn't match."])

    def test_form_is_invalid_if_password_is_empty(self):
        self.data['password'] = ''
        form = self.form_class(request=self.request, data=self.data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'password', ['This field is required.'])

    def test_form_is_invalid_if_confirming_password_is_empty(self):
        self.data['confirming_password'] = ''
        form = self.form_class(request=self.request, data=self.data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'confirming_password', ['This field is required.'])

    def test_form_creates_user_correctly(self):
        self.assertEqual(User.objects.count(), 0)

        form = self.form_class(request=self.request, data=self.data)
        self.assertTrue(form.is_valid())
        user = form.save()

        self.assertEqual(User.objects.count(), 1)
        User.objects.get(pk=user.pk)  # not raise
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))

    def test_form_doesnt_save_user_to_db_if_commit_is_false(self):
        self.assertEqual(User.objects.count(), 0)

        form = self.form_class(request=self.request, data=self.data)
        self.assertTrue(form.is_valid())
        form.save(commit=False)

        self.assertEqual(User.objects.count(), 0)

    def test_form_binds_worktable_to_user(self):
        form = self.form_class(request=self.request, data=self.data)
        form.is_valid()
        user = form.save()
        self.worktable.refresh_from_db()

        self.assertEqual(user.id, self.worktable.user.id)
