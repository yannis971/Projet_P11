import unittest
import time
from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import ui
from parameterized import parameterized


from .. import app


class FrontEndBookingUnitTests(LiveServerTestCase):
    """
    class to test front end booking
    """
    def create_app(self):
        app.config.from_object('webapp.tests_unitaires.config')
        return app

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.wait = ui.WebDriverWait(self.driver, 1000)

    def enter_text_field(self, selector, text):
        """
        Method to feed a text field
        """
        text_field = self.driver.find_element_by_id(selector)
        text_field.clear()
        text_field.send_keys(text)

    def submits_booking_form(self, places):
        """
        Method to feed en submit login form
        """
        self.enter_text_field("places", places)
        self.pause()
        self.driver.find_element_by_id("submit-form").click()

    @staticmethod
    def pause():
        """
        Method pause to let the user see the page
        """
        time.sleep(app.config['IMPLICIT_WAIT'])

    @parameterized.expand([
        ("Fall Classic 2021", "Iron Temple", "14"),
    ])
    def test_places_required_greater_than_competition_places(self, competition_name, club_name, places):
        """
        Front-End unit test in UI booking.html for case :
        places required greater than competition's number of places
        """
        self.driver.get(self.get_server_url() + "/book/" + f"{competition_name}/{club_name}")
        self.assertIn(f"Booking for {competition_name}", self.driver.title)
        places_required = self.driver.find_element_by_id("places")
        places_required.send_keys(places)
        places_required.send_keys(Keys.RETURN)
        assert "Number of places required is greater than competition's number of places" in self.driver.page_source
        self.pause()

    @parameterized.expand([
        ("Fall Classic 2021", "Iron Temple", "5"),
    ])
    def test_places_required_greater_than_club_points(self, competition_name, club_name, places):
        """
        Front-End unit test in UI booking.html for case :
        places required greater than club's points
        """
        self.driver.get(self.get_server_url() + "/book/" + f"{competition_name}/{club_name}")
        self.assertIn(f"Booking for {competition_name}", self.driver.title)
        places_required = self.driver.find_element_by_id("places")
        places_required.send_keys(places)
        places_required.send_keys(Keys.RETURN)
        assert "Number of places required is greater than club's points" in self.driver.page_source
        self.pause()

    @parameterized.expand([
        ("Spring Festival 2021", "Simply Lift", "13"),
    ])
    def test_places_required_greater_than_max_points(self, competition_name, club_name, places):
        """
        Front-End unit test in UI booking.html for case :
        places required greater than club's points
        """
        self.driver.get(self.get_server_url() + "/book/" + f"{competition_name}/{club_name}")
        self.assertIn(f"Booking for {competition_name}", self.driver.title)
        places_required = self.driver.find_element_by_id("places")
        places_required.send_keys(places)
        places_required.send_keys(Keys.RETURN)
        assert "Number of places required is greater than maximum places authorized" in self.driver.page_source
        self.pause()

    @parameterized.expand([
        ("Spring Festival 2021", "Simply Lift", "john@simplylift.co", "12", "Points available: 1"),
        ("Fall Classic 2021", "Iron Temple", "admin@irontemple.com",  "4", "Points available: 0"),
    ])
    def test_places_required_ok(self, competition_name, club_name, club_email, places, expected_club_points):
        """
        Front-End unit test in UI booking.html for case :
        places required is ok : between 1 and max(12, club['points']
        """
        # Book places
        self.driver.get(self.get_server_url() + "/book/" + f"{competition_name}/{club_name}")
        self.assertIn(f"Booking for {competition_name}", self.driver.title)
        self.submits_booking_form(places)
        # Wait for redirecting to showSummary page
        self.wait.until(lambda driver: self.driver.find_element_by_id("logout-link"))
        # After booking, check data in showSummary page
        self.assertIn("Summary | GUDLFT Registration", self.driver.title)
        self.assertIn(f"Welcome, {club_email}", self.driver.find_element_by_tag_name("h2").text)
        self.assertIn("Great-booking complete!", self.driver.page_source.__str__())
        self.assertIn(expected_club_points, self.driver.page_source.__str__())
        self.pause()

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()