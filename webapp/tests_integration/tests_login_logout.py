from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains
from flask import url_for
import time
import multiprocessing

from .. import app

opts = FirefoxOptions()
opts.add_argument("--headless")


class LoginLogoutTests(LiveServerTestCase):
    """
    class to test login and logout
    """
    # Allows fork process on macOS and Windows
    multiprocessing.set_start_method("fork")

    def create_app(self):
        app.config.from_object('webapp.tests_integration.config')
        return app

    def setUp(self):
        """Setup the test driver and create test users"""
        # Le navigateur est Firefox
        self.driver = webdriver.Firefox(options=opts)
        self.wait = ui.WebDriverWait(self.driver, 1000)

    def tearDown(self):
        self.driver.quit()

    def get_el(self, selector):
        return self.driver.find_element_by_css_selector(selector)

    def clicks_on_logout(self):
        """
        Method to click on logout
        """
        link = self.get_el("#logout-link")
        ActionChains(self.driver).click(link).perform()

    def enter_text_field(self, selector, text):
        """
        Method to feed a text field
        """
        text_field = self.get_el(selector)
        text_field.clear()
        text_field.send_keys(text)

    def sees_page(self, page, selector):
        """
        Method to check display of page
        """
        self.wait.until(lambda driver: self.get_el(selector))
        assert self.driver.current_url == url_for(page, _external=True)

    def submits_login_form(self, email):
        """
        Method to feed en submit login form
        """
        self.enter_text_field('#email', email)
        self.get_el('#login-button').click()

    def test_user_login_logout(self):
        """
        Use case :
        1. User sees index page
        2. User logins with a valid email
        3. User sees showSummary page
        4. User logouts
        5. User sees index page after redirecting
        """
        self.driver.get(self.get_server_url())
        self.sees_page('index', '#email')
        self.submits_login_form(app.config['VALID_USER_EMAIL'])
        self.sees_page('showSummary', '#logout-link')
        self.clicks_on_logout()
        self.wait.until(lambda driver: 'showSummary' not in self.driver.current_url)
        self.sees_page('index', '#email')

    def test_user_login_denied(self):
        """
        Use case :
        1. User sees index page
        2. User logins with a non valid email
        3. User sees index page after redirecting
        """
        self.driver.get(self.get_server_url())
        self.sees_page('index', '#email')
        self.submits_login_form(app.config['NON_VALID_USER_EMAIL'])
        self.wait.until(lambda driver: 'showSummary' not in self.driver.current_url)
        self.sees_page('index', '#email')
