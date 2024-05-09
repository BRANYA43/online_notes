from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase

from django.forms import ModelForm

from accounts import forms
from accounts.tests import TEST_EMAIL, TEST_PASSWORD
from notes import models as n_models

User = get_user_model()


class UserLoginFormTest(TestCase):
    def setUp(self) -> None:
        self.form_class = forms.UserLoginForm

        self.request = HttpRequest()

        self.data = {
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        }

        self.user = User.objects.create_user(**self.data)

    def test_form_is_invalid_if_email_is_empty(self):
        self.data['email'] = ''

        form = self.form_class(request=self.request, data=self.data)

        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'email', ['This field is required.'])

    def test_form_is_invalid_if_password_is_empty(self):
        self.data['password'] = ''

        form = self.form_class(request=self.request, data=self.data)

        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'password', ['This field is required.'])

    def test_form_is_invalid_if_authenticating_returns_none_user(self):
        self.data['email'] = 'non.existent@test.com'

        form = self.form_class(request=self.request, data=self.data)

        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, None, ['Please enter a correct email and password. Note: both fields may be case-sensitive.']
        )

    def test_form_caches_user_if_credentials_passed_authenticating(self):
        form = self.form_class(request=self.request, data=self.data)
        form.is_valid()

        self.assertEqual(form.cache_user.pk, self.user.pk)


class UserRegisterFormTest(TestCase):
    def setUp(self) -> None:
        self.form_class = forms.UserRegisterForm

        self.request = HttpRequest()
        self.request.session = self.client.session

        self.worktable = n_models.Worktable.objects.create(session_key=self.client.session.session_key)

        self.data = {
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
            'confirming_password': TEST_PASSWORD,
        }

    def test_form_inherit_ModelForm(self):
        self.assertTrue(issubclass(self.form_class, ModelForm))

    def test_form_is_invalid_if_confirming_password_and_password_arent_match(self):
        self.data['confirming_password'] = 'unmatch_password'

        form = self.form_class(self.request, self.data)

        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'confirming_password', ["The passwords didn't match."])

    def test_form_is_invalid_if_password_is_empty(self):
        self.data['password'] = ''

        form = self.form_class(self.request, self.data)

        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'password', ['This field is required.'])

    def test_form_is_invalid_if_confirming_password_is_empty(self):
        self.data['confirming_password'] = ''

        form = self.form_class(self.request, self.data)

        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'confirming_password', ['This field is required.'])

    def test_form_creates_user_correctly(self):
        self.assertEqual(User.objects.count(), 0)

        form = self.form_class(self.request, self.data)
        form.is_valid()
        user = form.save()

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))

    def test_form_doesnt_save_user_to_db_if_commit_is_false(self):
        self.assertEqual(User.objects.count(), 0)

        form = self.form_class(self.request, self.data)
        form.is_valid()
        form.save(commit=False)

        self.assertEqual(User.objects.count(), 0)

    def test_form_binds_worktable_to_user(self):
        self.assertIsNone(self.worktable.user)

        form = self.form_class(self.request, self.data)
        form.is_valid()
        user = form.save()
        self.worktable.refresh_from_db()

        self.assertEqual(user.id, self.worktable.user.id)
