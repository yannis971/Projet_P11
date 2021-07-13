from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains
from flask import url_for
import multiprocessing

from .. import app

opts = FirefoxOptions()
opts.add_argument("--headless")


class UsersTests(LiveServerTestCase):
    """
    class to test all functions from login to logout
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

    def clicks_on_book(self, competition_name, club_name):
        links = self.driver.find_elements_by_tag_name("a")
        url = self.get_server_url() + "/book/" + f"{competition_name}/{club_name}"
        for link in links:
            if link.get_attribute("href").replace("%20", " ") == url:
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

    def submits_booking_form(self, places):
        """
        Method to feed en submit login form
        """
        self.enter_text_field("#places", places)
        self.driver.find_element_by_id("submit-form").click()

    def test_user_login_logout(self):
        """
        Use case :
        1. User sees index page
        2. User logins with a valid email
        3. User sees showSummary page
        4. User books places for competitions
        5. User sees purchasePlaces page
        6. User logouts
        7. User sees index page after redirecting
        """
        self.driver.get(self.get_server_url())

        # User sees index page and then fills and submits email form
        self.sees_page('index', '#email')
        self.submits_login_form(app.config['VALID_EMAIL'])

        # User sees showSummary page and then clicks on competition link to book places
        self.sees_page('showSummary', '#logout-link')
        self.clicks_on_book(app.config['COMPETITION_NAME'], app.config['CLUB_NAME'])

        # User sees booking page and then fills places and submits booking form
        self.wait.until(lambda driver: self.get_el('#submit-form'))
        assert self.driver.current_url == url_for('book', competition=app.config['COMPETITION_NAME'],
                                                  club=app.config['CLUB_NAME'], _external=True)
        self.assertIn(f"Booking for {app.config['COMPETITION_NAME']}", self.driver.title)
        self.submits_booking_form(app.config['PLACES'])

        # User sees showSummary page redirected from purchasePlaces
        self.sees_page('purchasePlaces', '#logout-link')
        self.assertIn("Summary | GUDLFT Registration", self.driver.title)
        self.assertIn(f"Welcome, {app.config['VALID_EMAIL']}", self.driver.find_element_by_tag_name("h2").text)
        self.assertIn("Great-booking complete!", self.driver.page_source.__str__())
        self.assertIn(app.config['EXPECTED_POINTS'], self.driver.page_source.__str__())

        # User logs out
        self.clicks_on_logout()
        self.wait.until(lambda driver: 'showSummary' not in self.driver.current_url)
        self.sees_page('index', '#email')
        self.assertIn("You are logged out !", self.driver.page_source.__str__())


    def test_user_login_denied(self):
        """
        Use case :
        1. User sees index page
        2. User logins with a non valid email
        3. User sees index page after redirecting
        """
        self.driver.get(self.get_server_url())
        self.sees_page('index', '#email')
        self.submits_login_form(app.config['NON_VALID_EMAIL'])
        self.wait.until(lambda driver: 'showSummary' not in self.driver.current_url)
        self.sees_page('index', '#email')
        self.assertIn(f"Sorry, that email {app.config['NON_VALID_EMAIL']} was not found.", self.driver.page_source.__str__())
