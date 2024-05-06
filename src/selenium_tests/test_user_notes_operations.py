from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.color import Color

from accounts.forms import User
from accounts.tests import TEST_EMAIL, TEST_PASSWORD
from notes.models import Worktable, Category, Note
from selenium_tests import FunctionalTestCase


class RegisteredUserNotesOperationsTest(FunctionalTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email = TEST_EMAIL
        self.password = TEST_PASSWORD

        user = User.objects.create_user(email=self.email, password=self.password)
        self.worktable = Worktable.objects.create(user=user)

        self.category = Category.objects.create(worktable=self.worktable, title='Category #1', color='#ff0000')

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
        color = Color.from_string(self.category.color)
        card_body = card.find_element(By.CLASS_NAME, 'card-body')

        self.assertEqual(card_body.get_attribute('style'), f'color: {color.rgb};')

    def test_user_can_edit_recently_created_note_without_choosing_it_in_note_list(self):
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
        # User checks a note list, that have a created new note.
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_note_value_in_the_card(
            card,
            note_title=self.title,
        )

        # User changes the title of a recently created note in the same form
        new_title = 'New title for a recently created note'
        note_form = self.browser.find_element(value='note_form')
        self.send_form(
            note_form,
            select_fields=('id_category',),
            id_category=str(self.category.id),
            id_title=new_title,
        )

        # User checks a note list to confirms that title changed
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_note_value_in_the_card(
            card,
            category_title=self.category.title,
            note_title=new_title,
        )

        # User checks a note, that has colored text by category color
        color = Color.from_string(self.category.color)
        card_body = card.find_element(By.CLASS_NAME, 'card-body')

        self.assertEqual(card_body.get_attribute('style'), f'color: {color.rgb};')

    def test_user_can_edit_choice_note_from_note_list(self):
        note = Note.objects.create(worktable=self.worktable, title='Note #1', text='Some Text')

        # User enters to site
        self.enter_to_site()

        # User logins to site
        self.login_user_through_selenium()

        # User sees a note in the note list and click on edit button
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_note_value_in_the_card(
            card,
            note_title=note.title,
        )
        card.find_element(value='edit').click()

        # User sees a full form by info from note
        self.wait_for(
            lambda: self.browser.find_element(value='note_form').find_element(value='id_title').get_attribute('value'),
            note.title,
        )

        # User changes a title
        new_title = 'Changed Title'
        note_form = self.browser.find_element(value='note_form')
        self.send_form(
            note_form,
            select_fields=('id_category',),
            id_category=str(self.category.id),
            id_title=new_title,
        )

        # User checks a note in the note list
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_note_value_in_the_card(
            card,
            category_title=self.category.title,
            note_title=new_title,
        )

        # User checks a note, that has colored text by category color
        color = Color.from_string(self.category.color)
        card_body = card.find_element(By.CLASS_NAME, 'card-body')

        self.assertEqual(card_body.get_attribute('style'), f'color: {color.rgb};')

    def test_user_can_deletes_choice_note_from_note_list(self):
        note = Note.objects.create(worktable=self.worktable, title='Note #1', text='Some Text')

        # User enters to site
        self.enter_to_site()

        # User logins to site
        self.login_user_through_selenium()

        # User sees a note in the note list and click on edit button
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_note_value_in_the_card(
            card,
            note_title=note.title,
        )
        card.find_element(value='delete').click()

        # User sees empty note list
        self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_elements(By.CLASS_NAME, 'card'),
            expected_value=[],
        )


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

    def get_worktable(self):
        self.enter_to_site()
        return Worktable.objects.first()

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
        worktable = self.get_worktable()
        category = Category.objects.create(worktable=worktable, title='Category #1', color='#ff0000')

        # User enter to site
        self.enter_to_site()

        # User finds note form and input some text
        note_form = self.browser.find_element(value='note_form')
        self.send_form(
            note_form,
            select_fields=('id_category',),
            id_category=str(category.id),
            id_title=self.title,
            id_text=self.text,
        )

        # User checks left side and sees a note list, that have a created new note.
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )

        self.check_note_value_in_the_card(
            card,
            category_title=category.title,
            note_title=self.title,
        )

        # User checks a note, that has colored text by category color
        color = Color.from_string(category.color)
        card_body = card.find_element(By.CLASS_NAME, 'card-body')

        self.assertEqual(card_body.get_attribute('style'), f'color: {color.rgb};')

    def test_each_user_sees_only_his_notes_and_doesnt_see_notes_of_others(self):
        rick_note_title = 'How did rick become pickle?'

        # Rick enter to site
        self.enter_to_site()

        # Rick finds note form and input some text
        note_form = self.browser.find_element(value='note_form')
        self.send_form(
            note_form,
            id_title=rick_note_title,
            id_text='',
        )

        # Rick checks a note list, that have a created new note.
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )

        self.check_note_value_in_the_card(
            card,
            note_title=rick_note_title,
        )

        # Rick exits from site
        self.browser.quit()

        # Prepare new browser for Morty
        self.browser = self.get_browser()

        # Morty enters to site
        self.enter_to_site()

        # Morty checks a note list and doesn't see a note that was created by Rick
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card')

    def test_user_can_edit_recently_created_note_without_choosing_it_in_note_list(self):
        # User enters to site
        self.enter_to_site()

        # User finds note form and input some text
        note_form = self.browser.find_element(value='note_form')
        self.send_form(
            note_form,
            id_title=self.title,
            id_text=self.text,
        )
        # User checks a note list, that have a created new note.
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_note_value_in_the_card(
            card,
            note_title=self.title,
        )

        # User changes the title of a recently created note in the same form
        new_title = 'New title for a recently created note'
        note_form = self.browser.find_element(value='note_form')
        self.send_form(
            note_form,
            id_title=new_title,
        )

        # User checks a note list to confirms that title changed
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_note_value_in_the_card(
            card,
            note_title=new_title,
        )

    def test_user_can_edit_choice_note_from_note_list(self):
        note = Note.objects.create(worktable=self.get_worktable(), title='Note #1', text='Some Text')

        # User enters to site
        self.enter_to_site()

        # User sees a note in the note list and click on edit button
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_note_value_in_the_card(
            card,
            note_title=note.title,
        )
        card.find_element(value='edit').click()

        # User sees a full form by info from note
        self.wait_for(
            lambda: self.browser.find_element(value='note_form').find_element(value='id_title').get_attribute('value'),
            note.title,
        )

        # User changes a title
        new_title = 'Changed Title'
        note_form = self.browser.find_element(value='note_form')
        self.send_form(
            note_form,
            id_title=new_title,
        )

        # User checks a note in the note list
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_note_value_in_the_card(
            card,
            note_title=new_title,
        )

    def test_user_can_deletes_choice_note_from_note_list(self):
        note = Note.objects.create(worktable=self.get_worktable(), title='Note #1', text='Some Text')

        # User enters to site
        self.enter_to_site()

        # User sees a note in the note list and click on edit button
        card = self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_note_value_in_the_card(
            card,
            note_title=note.title,
        )
        card.find_element(value='delete').click()

        # User sees empty note list
        self.wait_for(
            lambda: self.browser.find_element(value='note_list').find_elements(By.CLASS_NAME, 'card'),
            expected_value=[],
        )
