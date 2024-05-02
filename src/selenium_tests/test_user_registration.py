from selenium.webdriver.common.by import By

from selenium_tests import FunctionalTestCase


class UserRegistrationTest(FunctionalTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email = 'rick.sanchez@test.com'
        self.password = 'qwe123!@#'

    def test_user_can_register(self):
        # User enters to the site.
        self.browser.get(self.live_server_url)

        # User clicks on "Sing Up" link in navbar.
        navbar = self.wait_for(
            lambda: self.browser.find_element(value='navbar'),
        )
        navbar.find_element(By.NAME, 'registration_link').click()

        # User inputs credentials to appeared modal form to register.
        modal_form = self.browser.find_element(value='modal_registration_form')
        modal_form.find_element(value='id_email').send_keys(self.email)
        modal_form.find_element(value='id_password').send_keys(self.password)
        modal_form.find_element(value='id_confirming_password').send_keys(self.password)
        modal_form.find_element(value='registration_submit_btn').click()

        # User clicks on "Sing In" link in navbar.
        self.wait_for(
            lambda: navbar.find_element(By.NAME, 'login_link').click(),
        )

        # User inputs credentials to appeared modal form to login.
        modal_form = self.browser.find_element(value='modal_login_form')
        self.wait_for(lambda: modal_form.find_element(value='id_email').send_keys(self.email))
        modal_form.find_element(value='id_password').send_keys(self.password)
        modal_form.find_element(value='login_submit_btn').click()

        # User checks navbar to confirm he was entered to his account.
        email = self.wait_for(
            lambda: self.browser.find_element(value='navbar').find_element(value='user').text,
        )

        self.assertEqual(email, self.email)
