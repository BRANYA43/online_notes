import re

from django.core import mail
from selenium.webdriver.common.by import By
from selenium_tests import FunctionalTestCase


class UserRegistrationTest(FunctionalTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url_pattern = re.compile(r'^http(s)?://.+/account/confirm_email/.+/.+/$')
        self.email = 'rick.sanchez@test.com'
        self.password = 'qwe123!@#'

    def test_user_can_register_to_use_only_email(self):
        # User enters to the site.
        self.browser.get(self.live_server_url)

        # User finds a "Sing Up" button in the navbar and he clicks on it.
        navbar = self.wait_for(
            lambda: self.browser.find_element(value='navbar'),
        )
        login_link = navbar.find_element(By.NAME, 'registration_link')
        login_link.click()

        # User sees a modal form and enter an email and a password to the form field.
        # After he clicks on the "Sing Up" button in the modal.
        modal_form = self.browser.find_element(value='modal_registration_form')
        email_input = modal_form.find_element(value='email')
        email_input.send_keys(self.email)
        password_input = modal_form.find_element(value='password')
        password_input.send_keys(self.password)
        modal_form.find_element(By.NAME, 'submit_btn')

        # User sees modal msg, there is saying, his email got msg with instruction
        # for confirming his email
        modal_msg = self.browser.find_element(value='modal_registration_msg')
        text = modal_msg.find_element(By.TAG_NAME, 'p').text
        self.assertEqual(text, 'We sent instruction to your email, that you will confirmed your email.')

        # User visits to his email and click on link for confirming the email.
        msg = mail.outbox.pop(0)
        url = self.url_pattern.search(msg)
        self.browser.get(url)

        # User follows to home page and sees modal msg about success confirming email
        modal_msg = self.wait_for(
            lambda: self.browser.find_element(value='modal_success_confirmed_email_msg'),
        )
        text = modal_msg.find_element(By.TAG_NAME, 'p').text
        self.assertEqual(text, 'You confirmed email successfully. Now, you can sing in to your account. Sing in.')

        # User log in to account
        navbar = self.browser.find_element(value='navbar')
        login_link = navbar.find_element(By.NAME, 'login_link')
        login_link.click()

        modal_form = self.browser.find_element(value='modal_login_from')
        email_input = modal_form.find_element(value='email')
        email_input.send_keys(self.email)
        password_input = modal_form.find_element(value='password')
        password_input.send_keys(self.password)
        modal_form.find_element(By.NAME, 'submit_btn')

        # User checks navbar to be convinced that he entered to his account
        navbar = self.wait_for(self.browser.find_element(value='navbar'))
        email = navbar.find_element(value='user_email').text

        self.assertEqual(email, self.email)
