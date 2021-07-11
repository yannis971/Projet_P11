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

    @staticmethod
    def pause():
        """
        Method pause to let the user see the page
        """
        time.sleep(app.config['IMPLICIT_WAIT'])

    @parameterized.expand([
        ("Fall Classic", "Iron Temple", "14"),
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
        ("Fall Classic", "Iron Temple", "5"),
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

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()