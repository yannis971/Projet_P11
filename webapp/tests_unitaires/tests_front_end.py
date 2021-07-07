import unittest
from parameterized import parameterized
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class FrontEndBookingUnitTests(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    @parameterized.expand([
        ("Fall Classic", "Iron Temple", "14"),
    ])
    def test_places_required_greater_than_competition_places(self, competition_name, club_name, places):
        """
        Front-End unit test in UI booking.html for case :
        places required greater than competition's number of places
        """
        driver = self.driver
        driver.get(f"http://127.0.0.1:5000/book/{competition_name}/{club_name}")
        self.assertIn(f"Booking for {competition_name}", driver.title)
        places_required = driver.find_element_by_id("places")
        places_required.send_keys(places)
        places_required.send_keys(Keys.RETURN)
        assert "Number of places required is greater than competition's number of places" in driver.page_source

    @parameterized.expand([
        ("Fall Classic", "Iron Temple", "5"),
    ])
    def test_places_required_greater_than_club_points(self, competition_name, club_name, places):
        """
        Front-End unit test in UI booking.html for case :
        places required greater than club's points
        """
        driver = self.driver
        driver.get(f"http://127.0.0.1:5000/book/{competition_name}/{club_name}")
        self.assertIn(f"Booking for {competition_name}", driver.title)
        places_required = driver.find_element_by_id("places")
        places_required.send_keys(places)
        places_required.send_keys(Keys.RETURN)
        assert "Number of places required is greater than club's points" in driver.page_source

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()