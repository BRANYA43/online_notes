from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By

from notes.models import Worktable
from selenium_tests import FunctionalTestCase


User = get_user_model()


class UserLogoutTest(FunctionalTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email = 'morty@test.com'
        self.password = 'qwe123!@#'
        self.data = {
            'email': self.email,
            'password': self.password,
        }
        self.user = User.objects.create_user(**self.data)
        self.create_worktable_for_user()

    def create_worktable_for_user(self):
        Worktable.objects.create(user=self.user)

    def test_user_can_logout(self):
        # User enters to the site.
        self.enter_to_site()

        # User login to the site
        navbar = self.wait_for(self.get_navbar)
        navbar.find_element(By.NAME, 'login_link').click()

        modal_form = self.browser.find_element(value='modal_login_form')
        self.send_form(
            modal_form,
            id_email=self.email,
            id_password=self.password,
        )

        # User clicks on his email link in navbar.
        user_email = self.wait_for(
            lambda: self.get_navbar().find_element(value='user'),
        )
        user_email.click()

        # In drop list user clicks on logout
        self.get_navbar().find_element(By.NAME, 'logout_link').click()

        # User checks navbar to confirm he was exits from his account.
        self.wait_for(
            lambda: self.get_navbar().find_element(By.NAME, 'registration_link'),
        )
