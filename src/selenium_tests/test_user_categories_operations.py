from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By

from accounts.tests import TEST_EMAIL, TEST_PASSWORD
from notes.models import Worktable
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

    def test_user_can_create_new_category(self):
        # User enter to site
        self.enter_to_site()

        # User logins to site
        self.login_user_through_selenium()

        # User finds a categories link and click on it
        self.get_navbar().find_element(By.NAME, 'categories_link').click()

        # User finds category form and input some data
        category_form = self.wait_for(lambda: self.browser.find_element(value='category_form'))
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

        # User logins to site
        self.login_user_through_selenium()

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

        # User changes the title and color of a recently created note in the same form
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

        # User changes the title and color of a recently created note in the same form
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
