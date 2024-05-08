from django.contrib.auth import get_user_model

from accounts.tests import TEST_EMAIL, TEST_PASSWORD
from notes.models import Worktable, Category
from selenium_tests import FunctionalTestCase


User = get_user_model()


class RegisteredUserCategoriesOperationsTest(FunctionalTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email = TEST_EMAIL
        self.password = TEST_PASSWORD

        user = User.objects.create_user(email=self.email, password=self.password)
        self.worktable = Worktable.objects.create(user=user)

        self.title = 'Category #1'
        self.color = '#00FF00'
        self.new_title = 'New Title'
        self.new_color = '#0000FF'

        self.login_user_through_selenium()

    def test_user_can_create_new_category(self):
        # User enter to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User inputs data to category form
        self.send_form(
            form=self.get_category_form(),
            id_title=self.title,
            id_color=self.color,
        )

        # User checks existing of a new category in the category list
        cards = self.wait_for(self.get_cards_from_category_list)
        self.check_category_card(
            card=cards[0],
            title=self.title,
            color=self.color,
        )

    def test_user_can_create_two_new_categories(self):
        # User enters to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User inputs data to the category form
        self.send_form(
            form=self.get_category_form(),
            id_title=self.title,
        )

        # User checks existing of a new category in the category list
        cards = self.wait_for(self.get_cards_from_category_list)
        self.check_category_card(
            card=cards[0],
            title=self.title,
        )

        # User clicks on "Create new"
        self.click_on_create_new_button()

        # User sees clean category form
        self.wait_for(
            lambda: self.get_category_form().find_element(value='id_title').get_attribute('value'),
            expected_value='',
        )

        # User inputs data to the category form for second new category
        second_title = 'Second category'
        self.send_form(
            form=self.get_category_form(),
            id_title=second_title,
        )

        # User checks existing of two new categorys in the category list
        self.wait_for(
            lambda: len(self.get_cards_from_category_list()),
            expected_value=2,
        )

        cards = self.get_cards_from_category_list()
        for card, title in zip(cards, (self.title, second_title)):
            self.check_category_card(
                card=card,
                title=title,
            )

    def test_user_can_edit_category_after_its_creation_in_same_form(self):
        # User enters to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User inputs data to the category form
        self.send_form(
            form=self.get_category_form(),
            id_title=self.title,
        )

        # User checks existing of a new category in the category list
        cards = self.wait_for(self.get_cards_from_category_list)
        self.check_category_card(
            card=cards[0],
            title=self.title,
        )

        # User edits category data
        self.send_form(form=self.get_category_form(), id_title=self.new_title, id_color=self.new_color)

        # User checks updating of a category data in the category list
        cards = self.wait_for(self.get_cards_from_category_list)
        self.check_category_card(
            card=cards[0],
            title=self.new_title,
            color=self.new_color,
        )

    def test_user_can_look_at_chosen_category_data(self):
        Category.objects.create(worktable=self.worktable, title=self.title, color=self.color)

        # User enters to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User clicks on "edit" button of chosen category
        self.wait_for(lambda: len(self.get_cards_from_category_list()), expected_value=1)
        cards = self.get_cards_from_category_list()
        self.click_on_edit_button(cards[0])

        # User sees title and text of chosen category
        self.wait_for(
            lambda: self.get_category_form().find_element(value='id_title').get_attribute('value'),
            expected_value=self.title,
        )
        self.assertEqual(
            self.get_category_form().find_element(value='id_color').get_attribute('value'),
            self.color,
        )

    def test_user_can_edit_chosen_category(self):
        Category.objects.create(worktable=self.worktable, title=self.title, color=self.color)

        # User enters to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User clicks on "edit" button of chosen category
        self.wait_for(lambda: len(self.get_cards_from_category_list()), expected_value=1)
        cards = self.get_cards_from_category_list()
        self.click_on_edit_button(cards[0])

        # User sees title and text of chosen category
        self.wait_for(
            lambda: self.get_category_form().find_element(value='id_title').get_attribute('value'),
            expected_value=self.title,
        )
        self.assertEqual(
            self.get_category_form().find_element(value='id_color').get_attribute('value'),
            self.color,
        )

        # User edits category data
        self.send_form(
            form=self.get_category_form(),
            id_title=self.new_title,
            id_color=self.new_color,
        )

        # User checks updating of a category data in the category list
        cards = self.wait_for(self.get_cards_from_category_list)
        self.check_category_card(
            card=cards[0],
            title=self.new_title,
            color=self.new_color,
        )

    def test_user_can_deletes_chosen_category(self):
        Category.objects.create(worktable=self.worktable, title=self.title, color=self.color)

        # User enters to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User clicks on "delete" button of chosen category
        self.wait_for(lambda: len(self.get_cards_from_category_list()), expected_value=1)
        cards = self.get_cards_from_category_list()
        self.click_on_delete_button(cards[0])

        # User sees empty category list
        self.wait_for(
            lambda: self.get_cards_from_category_list(),
            expected_value=[],
        )

    def test_user_can_create_new_category_after_work_with_another_category(self):
        Category.objects.create(worktable=self.worktable, title=self.title, color=self.color)

        # User enters to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User clicks on "edit" button of chosen category
        self.wait_for(lambda: len(self.get_cards_from_category_list()), expected_value=1)
        cards = self.get_cards_from_category_list()
        self.click_on_edit_button(cards[0])

        # User sees title and text of chosen category
        self.wait_for(
            lambda: self.get_category_form().find_element(value='id_title').get_attribute('value'),
            expected_value=self.title,
        )

        # User edits category data
        self.send_form(form=self.get_category_form(), id_title=self.new_title, id_color=self.new_color)

        # User checks updating of a category data in the category list
        cards = self.wait_for(self.get_cards_from_category_list)
        self.check_category_card(
            card=cards[0],
            title=self.new_title,
            color=self.new_color,
        )

        # User clicks on "Create new"
        self.click_on_create_new_button()

        # User sees clean category form
        self.wait_for(
            lambda: self.get_category_form().find_element(value='id_title').get_attribute('value'),
            expected_value='',
        )

        # User inputs data to the category form for second new category
        second_title = 'Second category'
        second_color = '#FF0000'
        self.send_form(
            form=self.get_category_form(),
            id_title=second_title,
            id_color=second_color,
        )

        # User checks existing of two new categories in the category list
        self.wait_for(
            lambda: len(self.get_cards_from_category_list()),
            expected_value=2,
        )

        cards = self.get_cards_from_category_list()
        for card, title, color in zip(cards, (self.new_title, second_title), (self.new_color, second_color)):
            self.check_category_card(card=card, title=title, color=color)


class AnonymousUserCategoriesOperationsTest(FunctionalTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.worktable = self.get_worktable()

        self.title = 'Category #1'
        self.color = '#00FF00'
        self.new_title = 'New Title'
        self.new_color = '#0000FF'

    def test_user_can_create_new_category(self):
        # User enter to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User inputs data to category form
        self.send_form(
            form=self.get_category_form(),
            id_title=self.title,
            id_color=self.color,
        )

        # User checks existing of a new category in the category list
        cards = self.wait_for(self.get_cards_from_category_list)
        self.check_category_card(
            card=cards[0],
            title=self.title,
            color=self.color,
        )

    def test_user_can_create_two_new_categories(self):
        # User enters to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User inputs data to the category form
        self.send_form(
            form=self.get_category_form(),
            id_title=self.title,
        )

        # User checks existing of a new category in the category list
        cards = self.wait_for(self.get_cards_from_category_list)
        self.check_category_card(
            card=cards[0],
            title=self.title,
        )

        # User clicks on "Create new"
        self.click_on_create_new_button()

        # User sees clean category form
        self.wait_for(
            lambda: self.get_category_form().find_element(value='id_title').get_attribute('value'),
            expected_value='',
        )

        # User inputs data to the category form for second new category
        second_title = 'Second category'
        self.send_form(
            form=self.get_category_form(),
            id_title=second_title,
        )

        # User checks existing of two new categorys in the category list
        self.wait_for(
            lambda: len(self.get_cards_from_category_list()),
            expected_value=2,
        )

        cards = self.get_cards_from_category_list()
        for card, title in zip(cards, (self.title, second_title)):
            self.check_category_card(
                card=card,
                title=title,
            )

    def test_user_can_edit_category_after_its_creation_in_same_form(self):
        # User enters to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User inputs data to the category form
        self.send_form(
            form=self.get_category_form(),
            id_title=self.title,
        )

        # User checks existing of a new category in the category list
        cards = self.wait_for(self.get_cards_from_category_list)
        self.check_category_card(
            card=cards[0],
            title=self.title,
        )

        # User edits category data
        self.send_form(form=self.get_category_form(), id_title=self.new_title, id_color=self.new_color)

        # User checks updating of a category data in the category list
        cards = self.wait_for(self.get_cards_from_category_list)
        self.check_category_card(
            card=cards[0],
            title=self.new_title,
            color=self.new_color,
        )

    def test_user_can_look_at_chosen_category_data(self):
        Category.objects.create(worktable=self.worktable, title=self.title, color=self.color)

        # User enters to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User clicks on "edit" button of chosen category
        self.wait_for(lambda: len(self.get_cards_from_category_list()), expected_value=1)
        cards = self.get_cards_from_category_list()
        self.click_on_edit_button(cards[0])

        # User sees title and text of chosen category
        self.wait_for(
            lambda: self.get_category_form().find_element(value='id_title').get_attribute('value'),
            expected_value=self.title,
        )
        self.assertEqual(
            self.get_category_form().find_element(value='id_color').get_attribute('value'),
            self.color,
        )

    def test_user_can_edit_chosen_category(self):
        Category.objects.create(worktable=self.worktable, title=self.title, color=self.color)

        # User enters to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User clicks on "edit" button of chosen category
        self.wait_for(lambda: len(self.get_cards_from_category_list()), expected_value=1)
        cards = self.get_cards_from_category_list()
        self.click_on_edit_button(cards[0])

        # User sees title and text of chosen category
        self.wait_for(
            lambda: self.get_category_form().find_element(value='id_title').get_attribute('value'),
            expected_value=self.title,
        )
        self.assertEqual(
            self.get_category_form().find_element(value='id_color').get_attribute('value'),
            self.color,
        )

        # User edits category data
        self.send_form(
            form=self.get_category_form(),
            id_title=self.new_title,
            id_color=self.new_color,
        )

        # User checks updating of a category data in the category list
        cards = self.wait_for(self.get_cards_from_category_list)
        self.check_category_card(
            card=cards[0],
            title=self.new_title,
            color=self.new_color,
        )

    def test_user_can_deletes_chosen_category(self):
        Category.objects.create(worktable=self.worktable, title=self.title, color=self.color)

        # User enters to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User clicks on "delete" button of chosen category
        self.wait_for(lambda: len(self.get_cards_from_category_list()), expected_value=1)
        cards = self.get_cards_from_category_list()
        self.click_on_delete_button(cards[0])

        # User sees empty category list
        self.wait_for(
            lambda: self.get_cards_from_category_list(),
            expected_value=[],
        )

    def test_user_can_create_new_category_after_work_with_another_category(self):
        Category.objects.create(worktable=self.worktable, title=self.title, color=self.color)

        # User enters to site
        self.enter_to_site()

        # User follows to a categories page
        self.follow_to_categories_page()

        # User clicks on "edit" button of chosen category
        self.wait_for(lambda: len(self.get_cards_from_category_list()), expected_value=1)
        cards = self.get_cards_from_category_list()
        self.click_on_edit_button(cards[0])

        # User sees title and text of chosen category
        self.wait_for(
            lambda: self.get_category_form().find_element(value='id_title').get_attribute('value'),
            expected_value=self.title,
        )

        # User edits category data
        self.send_form(form=self.get_category_form(), id_title=self.new_title, id_color=self.new_color)

        # User checks updating of a category data in the category list
        cards = self.wait_for(self.get_cards_from_category_list)
        self.check_category_card(
            card=cards[0],
            title=self.new_title,
            color=self.new_color,
        )

        # User clicks on "Create new"
        self.click_on_create_new_button()

        # User sees clean category form
        self.wait_for(
            lambda: self.get_category_form().find_element(value='id_title').get_attribute('value'),
            expected_value='',
        )

        # User inputs data to the category form for second new category
        second_title = 'Second category'
        second_color = '#FF0000'
        self.send_form(
            form=self.get_category_form(),
            id_title=second_title,
            id_color=second_color,
        )

        # User checks existing of two new categories in the category list
        self.wait_for(
            lambda: len(self.get_cards_from_category_list()),
            expected_value=2,
        )

        cards = self.get_cards_from_category_list()
        for card, title, color in zip(cards, (self.new_title, second_title), (self.new_color, second_color)):
            self.check_category_card(card=card, title=title, color=color)
