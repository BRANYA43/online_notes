from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By

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

        # User checks existing of two new notes in the category list
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

    def test_user_can_edit_note_after_its_creation_in_same_form(self):
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

    def test_user_can_edit_choice_category_from_category_list(self):
        category = Category.objects.create(worktable=self.worktable, title=self.title, color=self.color)

        # User enters to site
        self.enter_to_site()

        # User logins to site
        self.login_user_through_selenium()

        # User finds a categories link and click on it
        self.get_navbar().find_element(By.NAME, 'categories_link').click()

        card = self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_category_card(
            card,
            title=self.title,
            color=self.color,
        )
        card.find_element(value='edit').click()

        # User sees a full form by info from retrieved category
        self.wait_for(
            lambda: self.browser.find_element(value='category_form')
            .find_element(value='id_title')
            .get_attribute('value'),
            category.title,
        )

        # User changes a title
        new_title = 'New Category title'
        new_color = '#FF0000'
        category_form = self.browser.find_element(value='category_form')
        self.send_form(
            category_form,
            id_title=new_title,
            id_color=new_color,
        )

        # User checks a category list to confirms that title and color changed
        card = self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_category_card(
            card,
            title=new_title,
            color=new_color,
        )

    def test_user_can_deletes_choice_category_from_list(self):
        Category.objects.create(worktable=self.worktable, title=self.title, color=self.color)

        # User enters to site
        self.enter_to_site()

        # User logins to site
        self.login_user_through_selenium()

        # User finds a categories link and click on it
        self.get_navbar().find_element(By.NAME, 'categories_link').click()

        card = self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_category_card(
            card,
            title=self.title,
            color=self.color,
        )
        card.find_element(value='delete').click()

        # User sees empty category list
        self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_elements(By.CLASS_NAME, 'card'),
            expected_value=[],
        )

    def test_user_can_create_new_category_after_work_with_another_note(self):
        category = Category.objects.create(worktable=self.worktable, title='Category #1')

        # User enters to site
        self.enter_to_site()

        # User logins to site
        self.login_user_through_selenium()

        # User finds a categories link and click on it
        self.get_navbar().find_element(By.NAME, 'categories_link').click()

        # User sees a category in the category list and click on edit button
        card = self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_category_card(
            card,
            title=category.title,
        )
        card.find_element(value='edit').click()

        # User sees a full form by info from category
        self.wait_for(
            lambda: self.browser.find_element(value='category_form')
            .find_element(value='id_title')
            .get_attribute('value'),
            category.title,
        )

        # User clicks on create new button to create new category
        self.browser.find_element(value='create_new').click()

        # User sees the empty form
        self.wait_for(
            lambda: self.browser.find_element(value='category_form')
            .find_element(value='id_title')
            .get_attribute('value'),
            '',
        )

        # User enters new data
        new_title = 'New category Title'
        note_form = self.browser.find_element(value='category_form')
        self.send_form(
            note_form,
            id_title=new_title,
        )

        # User checks a new category in the category list
        card = self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_elements(By.CLASS_NAME, 'card')[1],
        )
        self.check_category_card(
            card,
            title=new_title,
        )


class AnonymousUserCategoriesOperationsTest(FunctionalTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.title = 'Category #1'
        self.color = '#00FF00'

    def test_user_can_create_new_category(self):
        # User enter to site
        self.enter_to_site()

        # User finds a categories link and click on it
        self.get_navbar().find_element(By.NAME, 'categories_link').click()

        # User finds category form and input some data
        category_form = self.browser.find_element(value='category_form')
        self.send_form(
            category_form,
            id_title=self.title,
            id_color=self.color,
        )

        # User checks a category list, that has a created new category
        card = self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_category_card(
            card,
            title=self.title,
            color=self.color,
        )

    def test_user_can_edit_recently_created_note(self):
        # User enters to site
        self.enter_to_site()

        # User finds a categories link and click on it
        self.get_navbar().find_element(By.NAME, 'categories_link').click()

        # User finds category form and input some data
        category_form = self.browser.find_element(value='category_form')
        self.send_form(
            category_form,
            id_title=self.title,
            id_color=self.color,
        )

        # User checks a category list, that has a created new category
        card = self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_category_card(
            card,
            title=self.title,
            color=self.color,
        )

        # User changes the title and color of a recently created category in the same form
        new_title = 'New Category title'
        new_color = '#FF0000'
        category_form = self.browser.find_element(value='category_form')
        self.send_form(
            category_form,
            id_title=new_title,
            id_color=new_color,
        )

        # User checks a category list to confirms that title and color changed
        card = self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_category_card(
            card,
            title=new_title,
            color=new_color,
        )

    def test_user_can_edit_choice_category_from_category_list(self):
        category = Category.objects.create(worktable=self.get_worktable(), title=self.title, color=self.color)

        # User enters to site
        self.enter_to_site()

        # User finds a categories link and click on it
        self.get_navbar().find_element(By.NAME, 'categories_link').click()

        card = self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_category_card(
            card,
            title=self.title,
            color=self.color,
        )
        card.find_element(value='edit').click()

        # User sees a full form by info from retrieved category
        self.wait_for(
            lambda: self.browser.find_element(value='category_form')
            .find_element(value='id_title')
            .get_attribute('value'),
            category.title,
        )

        # User changes a title
        new_title = 'New Category title'
        new_color = '#FF0000'
        category_form = self.browser.find_element(value='category_form')
        self.send_form(
            category_form,
            id_title=new_title,
            id_color=new_color,
        )

        # User checks a category list to confirms that title and color changed
        card = self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_category_card(
            card,
            title=new_title,
            color=new_color,
        )

    def test_user_can_deletes_choice_category_from_list(self):
        Category.objects.create(worktable=self.get_worktable(), title=self.title, color=self.color)

        # User enters to site
        self.enter_to_site()

        # User finds a categories link and click on it
        self.get_navbar().find_element(By.NAME, 'categories_link').click()

        card = self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_category_card(
            card,
            title=self.title,
            color=self.color,
        )
        card.find_element(value='delete').click()

        # User sees empty category list
        self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_elements(By.CLASS_NAME, 'card'),
            expected_value=[],
        )

    def test_user_can_create_new_category_after_work_with_another_note(self):
        category = Category.objects.create(worktable=self.get_worktable(), title='Category #1')

        # User enters to site
        self.enter_to_site()

        # User finds a categories link and click on it
        self.get_navbar().find_element(By.NAME, 'categories_link').click()

        # User sees a category in the category list and click on edit button
        card = self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_element(By.CLASS_NAME, 'card'),
        )
        self.check_category_card(
            card,
            title=category.title,
        )
        card.find_element(value='edit').click()

        # User sees a full form by info from category
        self.wait_for(
            lambda: self.browser.find_element(value='category_form')
            .find_element(value='id_title')
            .get_attribute('value'),
            category.title,
        )

        # User clicks on create new button to create new category
        self.browser.find_element(value='create_new').click()

        # User sees the empty form
        self.wait_for(
            lambda: self.browser.find_element(value='category_form')
            .find_element(value='id_title')
            .get_attribute('value'),
            '',
        )

        # User enters new data
        new_title = 'New Category Title'
        note_form = self.browser.find_element(value='category_form')
        self.send_form(
            note_form,
            id_title=new_title,
        )

        # User checks a new category in the category list
        card = self.wait_for(
            lambda: self.browser.find_element(value='category_list').find_elements(By.CLASS_NAME, 'card')[1],
        )
        self.check_category_card(
            card,
            title=new_title,
        )
