from datetime import timedelta

from django.utils import timezone

from accounts.forms import User
from accounts.tests import TEST_EMAIL, TEST_PASSWORD
from notes.filters import NoteFilter
from notes.models import Worktable, Category, Note
from selenium_tests import FunctionalTestCase


class RegisteredUserNotesOperationsTest(FunctionalTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email = TEST_EMAIL
        self.password = TEST_PASSWORD
        self.filter_class = NoteFilter

        user = User.objects.create_user(email=self.email, password=self.password)
        self.worktable = Worktable.objects.create(user=user)
        self.category = Category.objects.create(worktable=self.worktable, title='Category #1', color='#ff0000')

        self.title = 'What do I do to find a job?'
        self.text = (
            'I have to:\n'
            '- be a Senior after finished a study;\n'
            '- have 5 years of experience within 1 year after finished a study;\n'
            '- ...; \n'
        )
        self.new_title = 'New Title'

        self.login_user_through_selenium()

    def test_user_can_create_new_note_without_category(self):
        # User enters to site
        self.enter_to_site()

        # User inputs data to the note form
        self.send_form(
            form=self.get_note_form(),
            id_title=self.title,
        )

        # User checks existing of a new note in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            title=self.title,
        )

    def test_user_can_create_new_note_with_category(self):
        # User enters to site
        self.enter_to_site()

        # User inputs data to the note form
        self.send_form(
            form=self.get_note_form(),
            select_fields=('id_category',),
            id_category=str(self.category.id),
            id_title=self.title,
        )

        # User checks existing of a new note in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            category=self.category.title,
            title=self.title,
            color=self.category.color,
        )

    def test_user_can_create_two_new_notes(self):
        # User enters to site
        self.enter_to_site()

        # User inputs data to the note form
        self.send_form(
            form=self.get_note_form(),
            id_title=self.title,
        )

        # User checks existing of a new note in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            title=self.title,
        )

        # User clicks on "Create new"
        self.click_on_create_new_button()

        # User sees clean note form
        self.wait_for(
            lambda: self.get_note_form().find_element(value='id_title').get_attribute('value'),
            expected_value='',
        )

        # User inputs data to the note form for second new note
        second_title = 'Second Note'
        self.send_form(
            form=self.get_note_form(),
            id_title=second_title,
        )

        # User checks existing of two new notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=2,
        )

        cards = self.get_cards_from_note_list()
        for card, title in zip(cards, (second_title, self.title)):
            self.check_note_card(
                card=card,
                title=title,
            )

    def test_user_can_edit_note_after_its_creation_in_same_form(self):
        # User enters to site
        self.enter_to_site()

        # User inputs data to the note form
        self.send_form(
            form=self.get_note_form(),
            id_title=self.title,
        )

        # User checks existing of a new note in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            title=self.title,
        )

        # User edits note data
        self.send_form(
            form=self.get_note_form(),
            select_fields=('id_category',),
            id_category=str(self.category.id),
            id_title=self.new_title,
        )

        # User checks updating of a note data in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            category=self.category.title,
            title=self.new_title,
            color=self.category.color,
        )

    def test_user_can_look_at_chosen_note_data(self):
        Note.objects.create(worktable=self.worktable, title=self.title, text=self.text)

        # User enters to site
        self.enter_to_site()

        # User clicks on "edit" button of chosen note
        self.wait_for(lambda: len(self.get_cards_from_note_list()), expected_value=1)
        cards = self.get_cards_from_note_list()
        self.click_on_edit_button(cards[0])

        # User sees title and text of chosen note
        self.wait_for(
            lambda: self.get_note_form().find_element(value='id_title').get_attribute('value'),
            expected_value=self.title,
        )
        self.assertEqual(
            self.get_note_form().find_element(value='id_text').get_attribute('value'),
            self.text,
        )

    def test_user_can_edit_chosen_note(self):
        Note.objects.create(worktable=self.worktable, title=self.title, text=self.text)

        # User enters to site
        self.enter_to_site()

        # User clicks on "edit" button of chosen note
        self.wait_for(lambda: len(self.get_cards_from_note_list()), expected_value=1)
        cards = self.get_cards_from_note_list()
        self.click_on_edit_button(cards[0])

        # User sees title and text of chosen note
        self.wait_for(
            lambda: self.get_note_form().find_element(value='id_title').get_attribute('value'),
            expected_value=self.title,
        )
        self.assertEqual(
            self.get_note_form().find_element(value='id_text').get_attribute('value'),
            self.text,
        )

        # User edits note data
        self.send_form(
            form=self.get_note_form(),
            select_fields=('id_category',),
            id_category=str(self.category.id),
            id_title=self.new_title,
        )

        # User checks updating of a note data in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            category=self.category.title,
            title=self.new_title,
            color=self.category.color,
        )

    def test_user_can_deletes_chosen_note(self):
        Note.objects.create(worktable=self.worktable, title=self.title)

        # User enters to site
        self.enter_to_site()

        # User clicks on "delete" button of chosen note
        self.wait_for(lambda: len(self.get_cards_from_note_list()), expected_value=1)
        cards = self.get_cards_from_note_list()
        self.click_on_delete_button(cards[0])

        # User sees empty note list
        self.wait_for(
            lambda: self.get_cards_from_note_list(),
            expected_value=[],
        )

    def test_user_can_archive_chosen_note(self):
        Note.objects.create(worktable=self.worktable, title=self.title)

        # User enters to site
        self.enter_to_site()

        # User clicks on "archive" button of chosen note
        self.wait_for(lambda: len(self.get_cards_from_note_list()), expected_value=1)
        cards = self.get_cards_from_note_list()
        self.click_on_archive_button(cards[0])

        # User sees changing color of archive button
        self.wait_for(
            lambda: self.get_cards_from_note_list()[0].find_element(value='archive').get_attribute('class'),
            included_value='btn-secondary',
        )

    def test_user_can_create_new_note_after_work_with_another_note(self):
        Note.objects.create(worktable=self.worktable, title=self.title)

        # User enters to site
        self.enter_to_site()

        # User clicks on "edit" button of chosen note
        self.wait_for(lambda: len(self.get_cards_from_note_list()), expected_value=1)
        cards = self.get_cards_from_note_list()
        self.click_on_edit_button(cards[0])

        # User sees title and text of chosen note
        self.wait_for(
            lambda: self.get_note_form().find_element(value='id_title').get_attribute('value'),
            expected_value=self.title,
        )

        # User edits note data
        self.send_form(
            form=self.get_note_form(),
            id_title=self.new_title,
        )

        # User checks updating of a note data in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            title=self.new_title,
        )

        # User clicks on "Create new"
        self.click_on_create_new_button()

        # User sees clean note form
        self.wait_for(
            lambda: self.get_note_form().find_element(value='id_title').get_attribute('value'),
            expected_value='',
        )

        # User inputs data to the note form for second new note
        second_title = 'Second Note'
        self.send_form(
            form=self.get_note_form(),
            id_title=second_title,
        )

        # User checks existing of two new notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=2,
        )

        cards = self.get_cards_from_note_list()
        for card, title in zip(cards, (second_title, self.new_title)):
            self.check_note_card(
                card=card,
                title=title,
            )

    def test_user_can_filter_notes_by_status(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

        # User filter notes by active status
        self.send_filter(
            form=self.get_filter_form(),
            select_fields=('id_status',),
            id_status=self.filter_class.Status.ACTIVE,
        )

        # User sees 4 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=4,
        )

        # User filter notes by archived status
        self.send_filter(
            form=self.get_filter_form(),
            select_fields=('id_status',),
            id_status=self.filter_class.Status.ARCHIVED,
        )

        # User sees 4 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=1,
        )

    def test_user_can_filter_notes_by_category(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

        # User filter notes by category
        self.send_filter(
            form=self.get_filter_form(),
            select_fields=('id_category',),
            id_category=self.category.id,
        )

        # User sees 4 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=4,
        )

    def test_user_can_filter_notes_by_quantity_words_range(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

        # User filter notes by words range
        self.send_filter(
            form=self.get_filter_form(),
            range_fields=('id_words',),
            id_words=(0, 30),
        )

        # User sees 3 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=3,
        )

    def test_user_can_filter_notes_by_quantity_unique_words_range(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

        # User filter notes by unique words range
        self.send_filter(
            form=self.get_filter_form(),
            range_fields=('id_unique_words',),
            id_unique_words=(0, 3),
        )

        # User sees 3 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=3,
        )

    def test_user_can_filter_notes_by_date_range(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

        # User filter notes by date range
        start = timezone.now() + timedelta(days=1)
        start = start.strftime('%Y-%m-%d')
        end = timezone.now() + timedelta(days=2)
        end = end.strftime('%Y-%m-%d')
        self.send_filter(
            form=self.get_filter_form(),
            range_fields=('id_created',),
            id_created=(start, end),
        )

        # User sees 3 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=1,
        )

    def test_user_reset_filter_form(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

        # User filter notes by words range
        self.send_filter(
            form=self.get_filter_form(),
            range_fields=('id_words',),
            id_words=(0, 3),
        )

        # User sees 3 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=0,
        )

        # User reset form
        self.click_on_reset_filters_buttons()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

    def test_every_user_has_only_his_notes(self):
        # Rick enters to site
        self.enter_to_site()

        # Rick inputs data to the note form to create it
        self.send_form(
            form=self.get_note_form(),
            id_title=self.title,
        )

        # Rick checks existing of a new note in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            title=self.title,
        )

        # Rick exits from the site
        self.browser.quit()

        # Morty enter to site
        self.browser = self.get_browser()
        self.enter_to_site()

        # Morty doesn't see Rick's note
        cards = self.wait_for(
            lambda: self.get_cards_from_note_list(),
            expected_value=[],
        )


class AnonymousUserNotesOperationsTest(FunctionalTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email = TEST_EMAIL
        self.password = TEST_PASSWORD
        self.filter_class = NoteFilter

        self.worktable = self.get_worktable()
        self.category = Category.objects.create(worktable=self.worktable, title='Category #1', color='#ff0000')

        self.title = 'What do I do to find a job?'
        self.text = (
            'I have to:\n'
            '- be a Senior after finished a study;\n'
            '- have 5 years of experience within 1 year after finished a study;\n'
            '- ...; \n'
        )
        self.new_title = 'New Title'

    def test_user_can_create_new_note_without_category(self):
        # User enters to site
        self.enter_to_site()

        # User inputs data to the note form
        self.send_form(
            form=self.get_note_form(),
            id_title=self.title,
        )

        # User checks existing of a new note in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            title=self.title,
        )

    def test_user_can_create_new_note_with_category(self):
        # User enters to site
        self.enter_to_site()

        # User inputs data to the note form
        self.send_form(
            form=self.get_note_form(),
            select_fields=('id_category',),
            id_category=str(self.category.id),
            id_title=self.title,
        )

        # User checks existing of a new note in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            category=self.category.title,
            title=self.title,
            color=self.category.color,
        )

    def test_user_can_create_two_new_notes(self):
        # User enters to site
        self.enter_to_site()

        # User inputs data to the note form
        self.send_form(
            form=self.get_note_form(),
            id_title=self.title,
        )

        # User checks existing of a new note in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            title=self.title,
        )

        # User clicks on "Create new"
        self.click_on_create_new_button()

        # User sees clean note form
        self.wait_for(
            lambda: self.get_note_form().find_element(value='id_title').get_attribute('value'),
            expected_value='',
        )

        # User inputs data to the note form for second new note
        second_title = 'Second Note'
        self.send_form(
            form=self.get_note_form(),
            id_title=second_title,
        )

        # User checks existing of two new notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=2,
        )

        cards = self.get_cards_from_note_list()
        for card, title in zip(cards, (second_title, self.title)):
            self.check_note_card(
                card=card,
                title=title,
            )

    def test_user_can_edit_note_after_its_creation_in_same_form(self):
        # User enters to site
        self.enter_to_site()

        # User inputs data to the note form
        self.send_form(
            form=self.get_note_form(),
            id_title=self.title,
        )

        # User checks existing of a new note in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            title=self.title,
        )

        # User edits note data
        self.send_form(
            form=self.get_note_form(),
            select_fields=('id_category',),
            id_category=str(self.category.id),
            id_title=self.new_title,
        )

        # User checks updating of a note data in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            category=self.category.title,
            title=self.new_title,
            color=self.category.color,
        )

    def test_user_can_look_at_chosen_note_data(self):
        Note.objects.create(worktable=self.worktable, title=self.title, text=self.text)

        # User enters to site
        self.enter_to_site()

        # User clicks on "edit" button of chosen note
        self.wait_for(lambda: len(self.get_cards_from_note_list()), expected_value=1)
        cards = self.get_cards_from_note_list()
        self.click_on_edit_button(cards[0])

        # User sees title and text of chosen note
        self.wait_for(
            lambda: self.get_note_form().find_element(value='id_title').get_attribute('value'),
            expected_value=self.title,
        )
        self.assertEqual(
            self.get_note_form().find_element(value='id_text').get_attribute('value'),
            self.text,
        )

    def test_user_can_edit_chosen_note(self):
        Note.objects.create(worktable=self.worktable, title=self.title, text=self.text)

        # User enters to site
        self.enter_to_site()

        # User clicks on "edit" button of chosen note
        self.wait_for(lambda: len(self.get_cards_from_note_list()), expected_value=1)
        cards = self.get_cards_from_note_list()
        self.click_on_edit_button(cards[0])

        # User sees title and text of chosen note
        self.wait_for(
            lambda: self.get_note_form().find_element(value='id_title').get_attribute('value'),
            expected_value=self.title,
        )
        self.assertEqual(
            self.get_note_form().find_element(value='id_text').get_attribute('value'),
            self.text,
        )

        # User edits note data
        self.send_form(
            form=self.get_note_form(),
            select_fields=('id_category',),
            id_category=str(self.category.id),
            id_title=self.new_title,
        )

        # User checks updating of a note data in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            category=self.category.title,
            title=self.new_title,
            color=self.category.color,
        )

    def test_user_can_deletes_chosen_note(self):
        Note.objects.create(worktable=self.worktable, title=self.title)

        # User enters to site
        self.enter_to_site()

        # User clicks on "delete" button of chosen note
        self.wait_for(lambda: len(self.get_cards_from_note_list()), expected_value=1)
        cards = self.get_cards_from_note_list()
        self.click_on_delete_button(cards[0])

        # User sees empty note list
        self.wait_for(
            lambda: self.get_cards_from_note_list(),
            expected_value=[],
        )

    def test_user_can_archive_chosen_note(self):
        Note.objects.create(worktable=self.worktable, title=self.title)

        # User enters to site
        self.enter_to_site()

        # User clicks on "archive" button of chosen note
        self.wait_for(lambda: len(self.get_cards_from_note_list()), expected_value=1)
        cards = self.get_cards_from_note_list()
        self.click_on_archive_button(cards[0])

        # User sees changing color of archive button
        self.wait_for(
            lambda: self.get_cards_from_note_list()[0].find_element(value='archive').get_attribute('class'),
            included_value='btn-secondary',
        )

    def test_user_can_create_new_note_after_work_with_another_note(self):
        Note.objects.create(worktable=self.worktable, title=self.title)

        # User enters to site
        self.enter_to_site()

        # User clicks on "edit" button of chosen note
        self.wait_for(lambda: len(self.get_cards_from_note_list()), expected_value=1)
        cards = self.get_cards_from_note_list()
        self.click_on_edit_button(cards[0])

        # User sees title and text of chosen note
        self.wait_for(
            lambda: self.get_note_form().find_element(value='id_title').get_attribute('value'),
            expected_value=self.title,
        )

        # User edits note data
        self.send_form(
            form=self.get_note_form(),
            id_title=self.new_title,
        )

        # User checks updating of a note data in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            title=self.new_title,
        )

        # User clicks on "Create new"
        self.click_on_create_new_button()

        # User sees clean note form
        self.wait_for(
            lambda: self.get_note_form().find_element(value='id_title').get_attribute('value'),
            expected_value='',
        )

        # User inputs data to the note form for second new note
        second_title = 'Second Note'
        self.send_form(
            form=self.get_note_form(),
            id_title=second_title,
        )

        # User checks existing of two new notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=2,
        )

        cards = self.get_cards_from_note_list()
        for card, title in zip(cards, (second_title, self.new_title)):
            self.check_note_card(
                card=card,
                title=title,
            )

    def test_user_can_filter_notes_by_status(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

        # User filter notes by active status
        self.send_filter(
            form=self.get_filter_form(),
            select_fields=('id_status',),
            id_status=self.filter_class.Status.ACTIVE,
        )

        # User sees 4 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=4,
        )

        # User filter notes by archived status
        self.send_filter(
            form=self.get_filter_form(),
            select_fields=('id_status',),
            id_status=self.filter_class.Status.ARCHIVED,
        )

        # User sees 4 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=1,
        )

    def test_user_can_filter_notes_by_category(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

        # User filter notes by category
        self.send_filter(
            form=self.get_filter_form(),
            select_fields=('id_category',),
            id_category=self.category.id,
        )

        # User sees 4 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=4,
        )

    def test_user_can_filter_notes_by_quantity_words_range(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

        # User filter notes by words range
        self.send_filter(
            form=self.get_filter_form(),
            range_fields=('id_words',),
            id_words=(0, 30),
        )

        # User sees 3 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=3,
        )

    def test_user_can_filter_notes_by_quantity_unique_words_range(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

        # User filter notes by unique words range
        self.send_filter(
            form=self.get_filter_form(),
            range_fields=('id_unique_words',),
            id_unique_words=(0, 3),
        )

        # User sees 3 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=3,
        )

    def test_user_can_filter_notes_by_date_range(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

        # User filter notes by date range
        start = timezone.now() + timedelta(days=1)
        start = start.strftime('%Y-%m-%d')
        end = timezone.now() + timedelta(days=2)
        end = end.strftime('%Y-%m-%d')
        self.send_filter(
            form=self.get_filter_form(),
            range_fields=('id_created',),
            id_created=(start, end),
        )

        # User sees 3 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=1,
        )

    def test_user_reset_filter_form(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

        # User filter notes by words range
        self.send_filter(
            form=self.get_filter_form(),
            range_fields=('id_words',),
            id_words=(0, 3),
        )

        # User sees 3 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=0,
        )

        # User reset form
        self.click_on_reset_filters_buttons()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_from_note_list()),
            expected_value=5,
        )

    def test_every_user_has_only_his_notes(self):
        # Rick enters to site
        self.enter_to_site()

        # Rick inputs data to the note form to create it
        self.send_form(
            form=self.get_note_form(),
            id_title=self.title,
        )

        # Rick checks existing of a new note in the note list
        cards = self.wait_for(self.get_cards_from_note_list)
        self.check_note_card(
            card=cards[0],
            title=self.title,
        )

        # Rick exits from the site
        self.browser.quit()

        # Morty enter to site
        self.browser = self.get_browser()
        self.enter_to_site()

        # Morty doesn't see Rick's note
        cards = self.wait_for(
            lambda: self.get_cards_from_note_list(),
            expected_value=[],
        )
