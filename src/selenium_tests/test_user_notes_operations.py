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
        cards = self.wait_for(self.get_cards_form_note_list)
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
        cards = self.wait_for(self.get_cards_form_note_list)
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
        cards = self.wait_for(self.get_cards_form_note_list)
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
            lambda: len(self.get_cards_form_note_list()),
            expected_value=2,
        )

        cards = self.get_cards_form_note_list()
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
        cards = self.wait_for(self.get_cards_form_note_list)
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
        cards = self.wait_for(self.get_cards_form_note_list)
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
        self.wait_for(lambda: len(self.get_cards_form_note_list()), expected_value=1)
        cards = self.get_cards_form_note_list()
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
        self.wait_for(lambda: len(self.get_cards_form_note_list()), expected_value=1)
        cards = self.get_cards_form_note_list()
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
        cards = self.wait_for(self.get_cards_form_note_list)
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
        self.wait_for(lambda: len(self.get_cards_form_note_list()), expected_value=1)
        cards = self.get_cards_form_note_list()
        self.click_on_delete_button(cards[0])

        # User sees empty note list
        self.wait_for(
            lambda: self.get_cards_form_note_list(),
            expected_value=[],
        )

    def test_user_can_archive_chosen_note(self):
        Note.objects.create(worktable=self.worktable, title=self.title)

        # User enters to site
        self.enter_to_site()

        # User clicks on "archive" button of chosen note
        self.wait_for(lambda: len(self.get_cards_form_note_list()), expected_value=1)
        cards = self.get_cards_form_note_list()
        self.click_on_archive_button(cards[0])

        # User sees changing color of archive button
        self.wait_for(
            lambda: self.get_cards_form_note_list()[0].find_element(value='archive').get_attribute('class'),
            included_value='btn-secondary',
        )

    def test_user_can_create_new_note_after_work_with_another_note(self):
        Note.objects.create(worktable=self.worktable, title=self.title)

        # User enters to site
        self.enter_to_site()

        # User clicks on "edit" button of chosen note
        self.wait_for(lambda: len(self.get_cards_form_note_list()), expected_value=1)
        cards = self.get_cards_form_note_list()
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
        cards = self.wait_for(self.get_cards_form_note_list)
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
            lambda: len(self.get_cards_form_note_list()),
            expected_value=2,
        )

        cards = self.get_cards_form_note_list()
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
            lambda: len(self.get_cards_form_note_list()),
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
            lambda: len(self.get_cards_form_note_list()),
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
            lambda: len(self.get_cards_form_note_list()),
            expected_value=1,
        )

    def test_user_can_filter_notes_by_category(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_form_note_list()),
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
            lambda: len(self.get_cards_form_note_list()),
            expected_value=4,
        )

    def test_user_can_filter_notes_by_quantity_words_range(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_form_note_list()),
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
            lambda: len(self.get_cards_form_note_list()),
            expected_value=3,
        )

    def test_user_can_filter_notes_by_quantity_unique_words_range(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_form_note_list()),
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
            lambda: len(self.get_cards_form_note_list()),
            expected_value=3,
        )

    def test_user_can_filter_notes_by_date_range(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_form_note_list()),
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
            lambda: len(self.get_cards_form_note_list()),
            expected_value=1,
        )

    def test_user_reset_filter_form(self):
        self.prepared_notes_for_filter()

        # User enters to site
        self.enter_to_site()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_form_note_list()),
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
            lambda: len(self.get_cards_form_note_list()),
            expected_value=0,
        )

        # User reset form
        self.click_on_reset_filters_buttons()

        # User sees 5 notes in the note list
        self.wait_for(
            lambda: len(self.get_cards_form_note_list()),
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
        cards = self.wait_for(self.get_cards_form_note_list)
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
            lambda: self.get_cards_form_note_list(),
            expected_value=[],
        )


#
#
# class AnonymousUserNotesOperationsTest(FunctionalTestCase):
#     def setUp(self) -> None:
#         super().setUp()
#         self.title = 'What do I do to find a job?'
#         self.text = """
#             I have to:
#                 - be a Senior after finished a study;
#                 - have 5 years of experience within 1 year after finished a study;
#                 - ...;
#             """
#
#     def check_note_value_in_the_card(self, card, note_title: str, category_title: str = None):
#         fields = card.find_elements(By.TAG_NAME, 'p')
#         if category_title is None:
#             category_title = '---'
#         self.assertRegex(fields[0].text, rf'Category: {category_title}')
#         self.assertRegex(fields[1].text, rf'Title: {note_title}')
#
#     def test_user_can_create_new_note_without_category(self):
#         # User enters to site
#         self.enter_to_site()
#
#         # User finds note form and input some text
#         note_form = self.browser.find_element(value='note_form')
#         self.send_form(
#             note_form,
#             id_title=self.title,
#             id_text=self.text,
#         )
#
#         # User checks left side and sees a note list, that have a created new note.
#         card = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
#         )
#         self.check_note_value_in_the_card(
#             card,
#             note_title=self.title,
#         )
#
#     def test_user_can_create_new_note_with_category(self):
#         worktable = self.get_worktable()
#         category = Category.objects.create(worktable=worktable, title='Category #1', color='#ff0000')
#
#         # User enter to site
#         self.enter_to_site()
#
#         # User finds note form and input some text
#         note_form = self.browser.find_element(value='note_form')
#         self.send_form(
#             note_form,
#             select_fields=('id_category',),
#             id_category=str(category.id),
#             id_title=self.title,
#             id_text=self.text,
#         )
#
#         # User checks left side and sees a note list, that have a created new note.
#         card = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
#         )
#
#         self.check_note_value_in_the_card(
#             card,
#             category_title=category.title,
#             note_title=self.title,
#         )
#
#         # User checks a note, that has colored text by category color
#         color = Color.from_string(category.color)
#         card_body = card.find_element(By.CLASS_NAME, 'card-body')
#
#         self.assertEqual(card_body.get_attribute('style'), f'color: {color.rgb};')
#
#     def test_each_user_sees_only_his_notes_and_doesnt_see_notes_of_others(self):
#         rick_note_title = 'How did rick become pickle?'
#
#         # Rick enter to site
#         self.enter_to_site()
#
#         # Rick finds note form and input some text
#         note_form = self.browser.find_element(value='note_form')
#         self.send_form(
#             note_form,
#             id_title=rick_note_title,
#             id_text='',
#         )
#
#         # Rick checks a note list, that have a created new note.
#         card = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
#         )
#
#         self.check_note_value_in_the_card(
#             card,
#             note_title=rick_note_title,
#         )
#
#         # Rick exits from site
#         self.browser.quit()
#
#         # Prepare new browser for Morty
#         self.browser = self.get_browser()
#
#         # Morty enters to site
#         self.enter_to_site()
#
#         # Morty checks a note list and doesn't see a note that was created by Rick
#         with self.assertRaises(NoSuchElementException):
#             self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card')
#
#     def test_user_can_edit_recently_created_note_without_choosing_it_in_note_list(self):
#         # User enters to site
#         self.enter_to_site()
#
#         # User finds note form and input some text
#         note_form = self.browser.find_element(value='note_form')
#         self.send_form(
#             note_form,
#             id_title=self.title,
#             id_text=self.text,
#         )
#         # User checks a note list, that have a created new note.
#         card = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
#         )
#         self.check_note_value_in_the_card(
#             card,
#             note_title=self.title,
#         )
#
#         # User changes the title of a recently created note in the same form
#         new_title = 'New title for a recently created note'
#         note_form = self.browser.find_element(value='note_form')
#         self.send_form(
#             note_form,
#             id_title=new_title,
#         )
#
#         # User checks a note list to confirms that title changed
#         card = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
#         )
#         self.check_note_value_in_the_card(
#             card,
#             note_title=new_title,
#         )
#
#     def test_user_can_edit_choice_note_from_note_list(self):
#         note = Note.objects.create(worktable=self.get_worktable(), title='Note #1', text='Some Text')
#
#         # User enters to site
#         self.enter_to_site()
#
#         # User sees a note in the note list and click on edit button
#         card = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
#         )
#         self.check_note_value_in_the_card(
#             card,
#             note_title=note.title,
#         )
#         card.find_element(value='edit').click()
#
#         # User sees a full form by info from note
#         self.wait_for(
#             lambda: self.browser.find_element(value='note_form').find_element(value='id_title').get_attribute('value'),
#             note.title,
#         )
#
#         # User changes a title
#         new_title = 'Changed Title'
#         note_form = self.browser.find_element(value='note_form')
#         self.send_form(
#             note_form,
#             id_title=new_title,
#         )
#
#         # User checks a note in the note list
#         card = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
#         )
#         self.check_note_value_in_the_card(
#             card,
#             note_title=new_title,
#         )
#
#     def test_user_can_deletes_choice_note_from_note_list(self):
#         note = Note.objects.create(worktable=self.get_worktable(), title='Note #1', text='Some Text')
#
#         # User enters to site
#         self.enter_to_site()
#
#         # User sees a note in the note list and click on delete button
#         card = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
#         )
#         self.check_note_value_in_the_card(
#             card,
#             note_title=note.title,
#         )
#         card.find_element(value='delete').click()
#
#         # User sees empty note list
#         self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_elements(By.CLASS_NAME, 'card'),
#             expected_value=[],
#         )
#
#     def test_user_can_archive_choice_note_from_note_list(self):
#         note = Note.objects.create(worktable=self.get_worktable(), title='Note #1', text='Some Text')
#
#         # User enters to site
#         self.enter_to_site()
#
#         # User sees a note in the note list and click on archive button
#         card = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
#         )
#         self.check_note_value_in_the_card(
#             card,
#             note_title=note.title,
#         )
#         card.find_element(value='archive').click()
#
#         # User sees changing of archiving button
#         self.wait_for(
#             lambda: self.browser.find_element(value='note_list')
#             .find_element(By.CLASS_NAME, 'card')
#             .find_element(value='archive')
#             .get_attribute('class'),
#             included_value='btn-secondary',
#         )
#
#     def test_user_can_create_new_note_after_work_with_another_note(self):
#         note = Note.objects.create(worktable=self.get_worktable(), title='Note #1', text='Some Text')
#
#         # User enters to site
#         self.enter_to_site()
#
#         # User sees a note in the note list and click on edit button
#         card = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
#         )
#         self.check_note_value_in_the_card(
#             card,
#             note_title=note.title,
#         )
#         card.find_element(value='edit').click()
#
#         # User sees a full form by info from note
#         self.wait_for(
#             lambda: self.browser.find_element(value='note_form').find_element(value='id_title').get_attribute('value'),
#             note.title,
#         )
#
#         # User clicks on create new button to create new note
#         self.browser.find_element(value='create_new').click()
#
#         # User sees the empty form
#         self.wait_for(
#             lambda: self.browser.find_element(value='note_form').find_element(value='id_title').get_attribute('value'),
#             '',
#         )
#
#         # User enters new data
#         new_title = 'New Note Title'
#         note_form = self.browser.find_element(value='note_form')
#         self.send_form(
#             note_form,
#             id_title=new_title,
#         )
#
#         # User checks a new note in the note list
#         card = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_element(By.CLASS_NAME, 'card'),
#         )
#         self.check_note_value_in_the_card(
#             card,
#             note_title=new_title,
#         )
#
#     def test_user_can_filter_notes(self):
#         category = Category.objects.create(worktable=self.get_worktable(), title='Category #1')
#         Note.objects.bulk_create(
#             [
#                 Note(
#                     worktable=self.get_worktable(),
#                     title=f'Note #{n}',
#                     category=category,
#                     words=n * 10,
#                     unique_words=n,
#                     is_archived=True if n == 3 else False,
#                 )
#                 for n, category in enumerate((category, category, None), start=1)
#             ]
#         )
#
#         # User enters to site
#         self.enter_to_site()
#
#         # User sees three notes in the note list
#         cards = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_elements(By.CLASS_NAME, 'card'),
#         )
#
#         self.assertEqual(len(cards), 3)
#         for expected_note, card in zip(Note.objects.all(), cards):
#             self.check_note_value_in_the_card(
#                 card,
#                 category_title=expected_note.category.title if expected_note.category else None,
#                 note_title=expected_note.title,
#             )
#
#         # User filters notes by status
#         filter_form = self.browser.find_element(value='filter_form')
#         status_select = Select(filter_form.find_element(value='id_status'))
#
#         # | Filtering by active status |
#         status_select.select_by_value(str(NoteFilter.Status.ACTIVE))
#
#         # User sees two filtered notes by active status
#         cards = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_elements(By.CLASS_NAME, 'card'),
#         )
#         self.assertEqual(len(cards), 2)
#         for expected_note, card in zip(Note.objects.filter(is_archived=False), cards):
#             self.check_note_value_in_the_card(
#                 card,
#                 category_title=expected_note.category.title if expected_note.category else None,
#                 note_title=expected_note.title,
#             )
#
#         # | Filtering by archive status |
#         status_select.select_by_value(str(NoteFilter.Status.ARCHIVED))
#
#         # User sees one filtered note by archive status
#         cards = self.wait_for(
#             lambda: self.browser.find_element(value='note_list').find_elements(By.CLASS_NAME, 'card'),
#         )
#         self.assertEqual(len(cards), 1)
#         for expected_note, card in zip(Note.objects.filter(is_archived=True), cards):
#             self.check_note_value_in_the_card(
#                 card,
#                 category_title=expected_note.category.title if expected_note.category else None,
#                 note_title=expected_note.title,
#             )
