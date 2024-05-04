from selenium.webdriver.common.by import By
from selenium.webdriver.support.color import Color

from accounts.forms import User
from accounts.tests import TEST_EMAIL, TEST_PASSWORD
from notes.models import Worktable, Category
from selenium_tests import FunctionalTestCase


class RegisteredUserNotesOperationsTest(FunctionalTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email = TEST_EMAIL
        self.password = TEST_PASSWORD

        user = User.objects.create_user(email=self.email, password=self.password)
        worktable = Worktable.objects.create(user=user)

        self.category = Category.objects.create(worktable=worktable, title='Category #1', color='#ff0000')

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

        self.wait_for(lambda: self.get_navbar().find_element(value='user'))

    def check_note_value_in_the_card(self, card, note_title: str, category_title: str = None):
        fields = card.find_elements(By.TAG_NAME, 'p')
        if category_title is None:
            category_title = '---'
        self.assertRegex(fields[0].text, rf'Category: {category_title}')
        self.assertRegex(fields[1].text, rf'Title: {note_title}')

    def test_user_can_create_new_note_without_category(self):
        # User enters to site
        self.enter_to_site()

        # User logins to site
        self.login_user_through_selenium()

        # User finds note form and input some text
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
        self.check_note_value_in_the_card(
            card,
            note_title=self.title,
        )

    def test_user_can_create_new_note_with_category(self):
        # User enters to site
        self.enter_to_site()

        # User logins to site
        self.login_user_through_selenium()

        # User finds note form and input some text
        note_form = self.browser.find_element(value='note_form')
        self.send_form(
            note_form,
            select_fields=('id_category',),
            id_category=str(self.category.id),
            id_title=self.title,
            id_text=self.text,
        )

        # User checks left side and sees a note list, that have a created new note.
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )

        self.check_note_value_in_the_card(
            card,
            category_title=self.category.title,
            note_title=self.title,
        )

        # User checks a note, that has colored text by category color
        card_body = card.find_element(By.CLASS_NAME, 'card-body')

        self.assertIsNotNone(card_body.get_attribute('style'), f'color: {Color.from_string(self.category.color).rgb}')


class AnonymousUserNotesOperationsTest(FunctionalTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email = TEST_EMAIL
        self.password = TEST_PASSWORD

        self.title = 'What do I do to find a job?'
        self.text = """
            I have to:
                - be a Senior after finished a study;
                - have 5 years of experience within 1 year after finished a study;
                - ...; 
            """

    def prepare_for_test(self):
        # Enter to site to create worktable for anonymous user
        self.enter_to_site()

        # Create category
        worktable = Worktable.objects.first()
        self.category = Category.objects.create(worktable=worktable, title='Category #1', color='#ff0000')

    def check_note_value_in_the_card(self, card, note_title: str, category_title: str = None):
        fields = card.find_elements(By.TAG_NAME, 'p')
        if category_title is None:
            category_title = '---'
        self.assertRegex(fields[0].text, rf'Category: {category_title}')
        self.assertRegex(fields[1].text, rf'Title: {note_title}')

    def test_user_can_create_new_note_without_category(self):
        # User enters to site
        self.enter_to_site()

        # User finds note form and input some text
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
        self.check_note_value_in_the_card(
            card,
            note_title=self.title,
        )

    def test_user_can_create_new_note_with_category(self):
        self.prepare_for_test()

        # User enter to site
        self.enter_to_site()

        # User finds note form and input some text
        note_form = self.browser.find_element(value='note_form')
        self.send_form(
            note_form,
            select_fields=('id_category',),
            id_category=str(self.category.id),
            id_title=self.title,
            id_text=self.text,
        )

        # User checks left side and sees a note list, that have a created new note.
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )

        self.check_note_value_in_the_card(
            card,
            category_title=self.category.title,
            note_title=self.title,
        )

        # User checks a note, that has colored text by category color
        card_body = card.find_element(By.CLASS_NAME, 'card-body')

        self.assertIsNotNone(card_body.get_attribute('style'), f'color: {Color.from_string(self.category.color).rgb}')
