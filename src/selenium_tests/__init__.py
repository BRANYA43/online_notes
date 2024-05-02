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

    @staticmethod
    @wait()
    def wait_for(fn: Callable):
        """Wait some time for a function to be completed or/and to return a value or exception."""
        return fn()

    def enter_to_site(self):
        self.browser.get(self.live_server_url)

    def get_navbar(self) -> WebElement:
        return self.browser.find_element(value='navbar')
