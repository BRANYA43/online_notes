import os
from datetime import timedelta
from functools import wraps
from time import time, sleep
from typing import Callable

from django.conf import settings
from django.test.utils import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from selenium.common import WebDriverException, ElementClickInterceptedException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.color import Color
from selenium.webdriver.support.select import Select
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver

from notes.models import Worktable, Note, Category


def wait(wait_time=5):
    """Wait some time for a function until it'll be completed and returns a value or exception."""

    def wrapper(fn: Callable):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            start_time = time()
            while True:
                try:
                    return fn(*args, **kwargs)
                except (AssertionError, WebDriverException, ElementClickInterceptedException) as e:
                    if time() - start_time > wait_time:
                        raise e
                    sleep(0.5)

        return wrapped

    return wrapper


def _find_geckodriver() -> str | None:
    """Find installed geckodriver"""
    path = settings.BASE_DIR / '.wdm/drivers/geckodriver/'
    for folder, _, filenames in os.walk(path):
        if 'geckodriver' in filenames:
            return os.path.join(folder, 'geckodriver')
    return None


def _get_path_to_geckodriver() -> str:
    """Return geckodriver path"""
    os.environ['WDM_LOCAL'] = '1'
    path = _find_geckodriver()
    if path is None:
        return GeckoDriverManager().install()
    return path


@override_settings(DEBUG=True)
class FunctionalTestCase(StaticLiveServerTestCase):
    def setUp(self) -> None:
        self.browser = self.get_browser()

    def tearDown(self) -> None:
        self.browser.quit()

    def get_browser(self) -> webdriver.Firefox:
        return webdriver.Firefox(service=self._get_service())

    @staticmethod
    def _get_service():
        path = _get_path_to_geckodriver()
        return Service(executable_path=path)

    @wait()
    def wait_for(self, fn: Callable, expected_value=None, included_value=None):
        """
        Wait for a function until it's completed or/and returns a value or exception.
        If expected_value is set, wait for a function until the returned value is equal
        expected_value or until it returns exception.
        If included_value is set, wait for a function until the returned value has
        included_value in or until it returns exception.
        """
        if expected_value is not None:
            result = fn()
            self.assertEqual(result, expected_value)
            return result
        elif included_value is not None:
            result = fn()
            self.assertIn(included_value, result)
            return result

        return fn()

    def enter_to_site(self):
        self.browser.get(self.live_server_url)

    def get_navbar(self) -> WebElement:
        return self.browser.find_element(value='navbar')

    def send_form(self, form: WebElement, select_fields=(), **inputs_with_value):
        """
        Send form to backend.
        :param select_fields: keys as ids for <input> tags
        :param inputs_with_value: key as id of <input> tag and value as value of <input> tag
        """
        for input_, value in inputs_with_value.items():
            input_elem = form.find_element(value=input_)
            if input_ in select_fields:
                Select(input_elem).select_by_value(value)
            elif input_ == 'id_color':
                action = ActionChains(self.browser)
                action.move_to_element(input_elem).click().key_down(Keys.CONTROL).send_keys('a').key_up(
                    Keys.CONTROL
                ).send_keys(value).perform()
            else:
                if input_elem.get_attribute('value'):
                    input_elem.clear()
                input_elem.send_keys(value)
        form.find_element(value='submit_btn').click()

    def send_filter(self, form: WebElement, select_fields=(), range_fields=(), **inputs_and_values):
        for input_, value in inputs_and_values.items():
            if input_ in range_fields:
                input_1 = form.find_element(value=f'{input_}_0')
                input_1.send_keys(value[0])
                input_2 = form.find_element(value=f'{input_}_1')
                input_2.send_keys(value[1])
                ActionChains(self.browser).move_by_offset(0, 0).click().perform()
            elif input_ in select_fields:
                Select(form.find_element(value=input_)).select_by_value(str(value))
            else:
                form.find_element(value=input_).send_keys(value)

    def login_user_through_selenium(self):
        self.enter_to_site()

        navbar = self.wait_for(self.get_navbar)
        navbar.find_element(By.NAME, 'login_link').click()

        modal_form = self.browser.find_element(value='modal_login_form')
        self.send_form(
            modal_form,
            id_email=self.email,
            id_password=self.password,
        )

        self.wait_for(lambda: self.get_navbar().find_element(value='user'))

    def get_worktable(self):
        self.enter_to_site()
        return Worktable.objects.first()

    def get_note_form(self) -> WebElement:
        return self.browser.find_element(value='note_form')

    def get_category_form(self) -> WebElement:
        return self.browser.find_element(value='category_form')

    def get_filter_form(self) -> WebElement:
        return self.browser.find_element(value='filter_form')

    def get_note_list(self) -> WebElement:
        return self.browser.find_element(value='note_list')

    def get_category_list(self) -> WebElement:
        return self.browser.find_element(value='category_list')

    def get_cards_form_note_list(self) -> list[WebElement]:
        return self.get_note_list().find_elements(By.CLASS_NAME, 'card')

    def get_cards_from_category_list(self) -> list[WebElement]:
        return self.get_category_list().find_elements(By.CLASS_NAME, 'card')

    def check_category_card(self, card, title, color='#FFFFFF'):
        color = Color.from_string(color)
        title_field = card.find_element(By.TAG_NAME, 'p')
        self.assertRegex(title_field.text, rf'Title: {title}')

        card_body = card.find_element(By.CLASS_NAME, 'card-body')
        self.assertIn(color.rgb, card_body.get_attribute('style'))

    def check_note_card(self, card, title: str, category: str = '---', color=None):
        fields = card.find_elements(By.TAG_NAME, 'p')
        self.assertRegex(fields[0].text, rf'Category: {category}')
        self.assertRegex(fields[1].text, rf'Title: {title}')

        if color:
            color = Color.from_string(color)
            card_body = card.find_element(By.CLASS_NAME, 'card-body')
            self.assertIn(color.rgb, card_body.get_attribute('style'))

    def click_on_create_new_button(self):
        self.browser.find_element(value='create_new').click()

    def click_on_edit_button(self, card: WebElement):
        card.find_element(value='edit').click()

    def click_on_delete_button(self, card: WebElement):
        card.find_element(value='delete').click()

    def click_on_archive_button(self, card: WebElement):
        card.find_element(value='archive').click()

    def click_on_reset_filters_buttons(self):
        self.get_filter_form().find_element(value='reset').click()

    def follow_to_categories_page(self):
        self.get_navbar().find_element(By.NAME, 'categories_link').click()
        self.wait_for(self.get_category_form)

    def prepared_notes_for_filter(self):
        worktable = self.get_worktable()
        self.category = Category.objects.create(worktable=worktable, title='Category #1')
        categories = tuple(self.category for _ in range(4)) + (None,)
        notes = [
            Note(
                worktable=worktable,
                title=f'Note #{n}',
                category=category,
                words=n * 10,
                unique_words=n,
                is_archived=True if n == 5 else False,
            )
            for n, category in enumerate(categories, start=1)
        ]
        notes = Note.objects.bulk_create(notes)
        notes[3].created = timezone.now() + timedelta(days=1)
        notes[3].save()
