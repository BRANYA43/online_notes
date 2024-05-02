from datetime import datetime
from time import sleep

from selenium.webdriver.common.by import By

from accounts.forms import User
from selenium_tests import FunctionalTestCase


class RegisteredUserWorkWithNotesTest(FunctionalTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email = 'bad.boy@test.com'
        self.password = 'qwe123!@#'
        self.data = {
            'email': self.email,
            'password': self.password,
        }
        self.user = User.objects.create_user(**self.data)

        self.title = 'What do I do to find a job?'
        self.text = """
            I have to:
                - be a Senior after finished a study;
                - have 5 years of experience within 1 year after finished a study;
                - ...; 
            """

    def login_user_through_selenium(self):
        navbar = self.wait_for(self.get_navbar)
        navbar.find_element(By.NAME, 'login_link').click()

        modal_form = self.browser.find_element(value='modal_login_form')
        self.send_form(
            modal_form,
            id_email=self.email,
            id_password=self.password,
        )

    def test_user_can_create_new_note_without_category(self):
        # User enters to site
        self.enter_to_site()

        # User logins to site
        self.login_user_through_selenium()

        # User finds note form and input some text
        sleep(1)  # TODO figure our a way to get around it
        note_form = self.browser.find_element(value='note_form')
        self.send_form(
            note_form,
            id_title=self.title,
            id_text=self.text,
        )

        # User checks left side and sees a note list, that have a created new note.
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )
        card_data = card.find_elements(By.TAG_NAME, 'p')
        title = card_data[0].text
        date = card_data[1].text

        self.assertEqual(title, self.title)
        self.assertEqual(date, datetime.now().strftime('%d.%m.$Y'))
