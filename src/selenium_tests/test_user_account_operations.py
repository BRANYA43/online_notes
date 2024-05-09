from django.contrib.auth import get_user_model

from accounts.tests import TEST_EMAIL, TEST_PASSWORD
from notes.models import Worktable
from selenium_tests import FunctionalTestCase

User = get_user_model()


class UserAccountOperationsTest(FunctionalTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email = TEST_EMAIL
        self.password = TEST_PASSWORD

    def test_user_can_register(self):
        # User enters to the site.
        self.enter_to_site()

        # User clicks on "Sing Up" link in navbar.
        self.click_on_sing_up()

        # User inputs credentials in the registration form
        self.send_form(
            form=self.get_registration_form(),
            id_email=self.email,
            id_password=self.password,
            id_confirming_password=self.password,
        )

        # User clicks on "Sing In" link in navbar.
        self.wait_for(self.click_on_sing_in)

        # User inputs credentials in the login form
        self.send_form(
            form=self.get_login_form(),
            id_email=self.email,
            id_password=self.password,
        )

        # User checks navbar to confirm he was entered to his account.
        self.wait_for(self.check_user_link)

    def test_user_can_logout(self):
        # | Prepare for Test |
        user = User.objects.create_user(email=self.email, password=self.password)
        Worktable.objects.create(user=user)

        # User enters to the site.
        self.enter_to_site()

        # User login to the site
        self.click_on_sing_in()

        self.send_form(
            form=self.get_login_form(),
            id_email=self.email,
            id_password=self.password,
        )

        # User clicks on his email link in navbar.
        self.wait_for(self.click_on_user_email)

        # In drop list user clicks on logout
        self.wait_for(self.click_on_user_logout)

        # User checks navbar to confirm he was exits from his account.
        self.wait_for(self.click_on_sing_up)
