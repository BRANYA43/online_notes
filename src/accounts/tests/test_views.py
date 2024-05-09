from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.tests import TEST_EMAIL, TEST_PASSWORD
from notes import models as notes_models

User = get_user_model()


class LogoutUserView(TestCase):
    def setUp(self) -> None:
        self.url = reverse('logout')
        self.data = {
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        }
        self.user = User.objects.create_user(**self.data)
        self.client.force_login(self.user)

    def test_view_logout_user_correctly(self):
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.pk))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.client.session.get('_auth_user_id'))


class LoginUserView(TestCase):
    def setUp(self) -> None:
        self.url = reverse('login')
        self.data = {
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        }

        self.user = User.objects.create_user(**self.data)

    def test_view_logins_user_correctly(self):
        self.assertIsNone(self.client.session.get('_auth_user_id'))

        response = self.client.post(self.url, self.data)

        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.pk))
        self.assertEqual(response.status_code, 200)

    def test_view_doesnt_login_user_if_credentials_are_invalid(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 400)

    def test_view_returns_emtpy_data_if_credentials_are_valid(self):
        response = self.client.post(self.url, self.data)
        data = response.json()

        self.assertFalse(data, msg="Data isn't empty.")

    def test_view_returns_errors_if_credentials_are_invalid(self):
        response = self.client.post(self.url, {})
        data = response.json()
        errors = data.get('errors')

        self.assertIsNotNone(errors)
        self.assertTrue(errors, msg='Data is empty.')


class RegisterUserView(TestCase):
    def setUp(self) -> None:
        self.url = reverse('register')

        self.worktable = notes_models.Worktable.objects.create(session_key=self.client.session.session_key)

        self.data = {
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
            'confirming_password': TEST_PASSWORD,
        }

    def test_view_registers_user_correctly(self):
        self.assertEqual(User.objects.count(), 0)

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.first()

        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))

    def test_view_doesnt_register_user_if_credentials_is_invalid(self):
        self.assertEqual(User.objects.count(), 0)

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)

    def test_view_doesnt_register_user_if_user_exists_with_such_credentials(self):
        data = self.data.copy()
        del data['confirming_password']
        User.objects.create_user(**data)

        self.assertEqual(User.objects.count(), 1)

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 1)

    def test_view_returns_errors_if_credentials_are_invalid(self):
        response = self.client.post(self.url, {})
        data = response.json()
        errors = data.get('errors')

        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(errors)
        self.assertTrue(errors, msg='Data is empty.')

    def test_view_returns_empty_data_if_credentials_are_valid(self):
        response = self.client.post(self.url, self.data)
        data = response.json()

        self.assertEqual(response.status_code, 201)
        self.assertFalse(data, msg="Data isn't empty.")
