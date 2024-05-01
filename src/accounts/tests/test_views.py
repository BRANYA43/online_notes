from django.test import TestCase
from django.urls import reverse

from accounts.forms import User


class RegisterUserView(TestCase):
    def setUp(self) -> None:
        self.url = reverse('register')
        self.email = 'fin.and.jake@test.com'
        self.password = 'qwe123!@#'
        self.data = {
            'email': self.email,
            'password': self.password,
            'confirming_password': self.password,
        }

    def test_view_registers_user_correctly(self):
        self.assertEqual(User.objects.count(), 0)

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.first()
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))

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

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 400)

    def test_view_returns_errors_if_credentials_are_invalid(self):
        response = self.client.post(self.url, {})
        data = response.json()
        errors = data.get('errors')

        self.assertIsNotNone(errors)
        self.assertTrue(errors, msg='Data is empty.')

    def test_view_returns_empty_data_if_credentials_are_valid(self):
        response = self.client.post(self.url, self.data)
        data = response.json()

        self.assertFalse(data, msg="Data isn't empty.")
