import os
from functools import wraps
from time import time, sleep
from typing import Callable

from django.conf import settings
from django.test.utils import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.common import WebDriverException, ElementClickInterceptedException
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver


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
    def wait_for(self, fn: Callable, expected_value=None):
        """
        Wait for a function until it's completed or/and returns a value or exception.
        if expected_value is set, wait for a function until returned value is
        equal expected value or until it return exception.
        """
        if expected_value is not None:
            result = fn()
            self.assertEqual(result, expected_value)
            return result
        return fn()

    def enter_to_site(self):
        self.browser.get(self.live_server_url)

    def get_navbar(self) -> WebElement:
        return self.browser.find_element(value='navbar')

    @staticmethod
    def send_form(form: WebElement, select_fields=(), **inputs_with_value):
        """
        Send form to backend.
        :param select_fields: keys as ids for <input> tags
        :param inputs_with_value: key as id of <input> tag and value as value of <input> tag
        """
        for input_, value in inputs_with_value.items():
            if input_ in select_fields:
                Select(form.find_element(value=input_)).select_by_value(value)
            else:
                input_elem = form.find_element(value=input_)
                if input_elem.get_attribute('value'):
                    input_elem.clear()
                input_elem.send_keys(value)
        form.find_element(value='submit_btn').click()
