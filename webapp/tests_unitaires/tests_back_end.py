import unittest
from contextlib import contextmanager
from flask import template_rendered
from parameterized import parameterized
from webapp import server


class ServerUnitTests(unittest.TestCase):

    def setUp(self) -> None:
        self.app = server.app
        self.app.config['TESTING'] = True
        self.app.config['DEBUG'] = False
        self.response = None
        self.template = None
        self.context = None

    def tearDown(self) -> None:
        pass

    @contextmanager
    def captured_templates(self):
        """
        Method to capture template rendered and context
        """
        recorded = []

        def record(sender, template, context, **extra):
            recorded.append((template, context))

        template_rendered.connect(record, self.app)
        try:
            yield recorded
        finally:
            template_rendered.disconnect(record, self.app)

    def verify_response_template_context(self, url, status_code, template_name,
                                         templates, method="GET", set_session=False, **data):
        """
        Method that generates response, template and context and then asserts
        every result is OK
        """
        if method == "GET":
            if set_session:
                with self.app.test_client() as test_client:
                    with test_client.session_transaction() as session_transaction:
                        for k, v in data.items():
                            session_transaction[k] = v
                    self.response = test_client.get(url, follow_redirects=True)
            else:
                self.response = self.app.test_client().get(url, follow_redirects=True)
        else:
            self.response = self.app.test_client().post(url, data=data,
                                                        follow_redirects=True)
        self.assertEqual(self.response.status_code, status_code)
        if status_code != 404:
            self.assertEqual(len(templates), 1)
            self.template, self.context = templates[0]
            self.assertEqual(self.template.name, template_name)

    def test_load_clubs(self):
        """
        Test function server.loadClubs()
        """
        load_clubs = server.loadClubs()
        self.assertIsInstance(load_clubs, list)
        for club in load_clubs:
            for key in ('name', 'email', 'points'):
                self.assertTrue(key in club)

    def test_load_competitions(self):
        """
        Test function server.loadCompetitions()
        """
        load_competitions = server.loadCompetitions()
        self.assertIsInstance(load_competitions, list)
        for competition in load_competitions:
            for key in ('name', 'date', 'numberOfPlaces'):
                self.assertTrue(key in competition)

    def test_get_club_by_name(self):
        """
        Test function server.get_club_by_name()
        """
        club = server.get_club_by_name("Simply Lift")
        self.assertEqual(club['name'], "Simply Lift")

    def test_get_competition_by_name(self):
        """
        Test function server.get_competition_by_name()
        """
        competition = server.get_competition_by_name("Spring Festival")
        self.assertEqual(competition['name'], "Spring Festival")

    @parameterized.expand([
        ("/", 200, "index.html"),
    ])
    def test_index(self, url, status_code, template_name):
        """
        Test function server.index()
        """
        with self.captured_templates() as templates:
            self.verify_response_template_context(url, status_code,
                                                  template_name, templates)

    @parameterized.expand([
        ("/showSummary", 200, "index.html", "john.doe@gmail.com"),
    ])
    def test_show_summary_index_error(self, url, status_code, template_name, email):
        """
        Test function server.showSummary() with an non valid email
        """
        with self.captured_templates() as templates:
            self.verify_response_template_context(url, status_code,
                                                  template_name, templates,
                                                  "POST", **dict(email=email,))
            self.assertRaises(IndexError)
            self.assertIn(b"Sorry, that email john.doe@gmail.com was not found.", self.response.data)

    @parameterized.expand([
        ("/showSummary", 200, "welcome.html", "admin@irontemple.com"),
    ])
    def test_show_summary(self, url, status_code, template_name, email):
        """
        Test function server.showSummary() with a valid email
        """
        with self.captured_templates() as templates:
            self.verify_response_template_context(url, status_code,
                                                  template_name, templates,
                                                  "POST", **dict(email=email,))
            club = self.context['club']
            self.assertEqual(club['email'], email)

    @parameterized.expand([
        ("/showSummary", 200, "welcome.html", "admin@irontemple.com"),
    ])
    def test_show_summary_get_method(self, url, status_code, template_name, email):
        """
        Test function server.showSummary() with a valid email and get method
        """
        with self.captured_templates() as templates:
            self.verify_response_template_context(url, status_code,
                                                  template_name, templates,
                                                  method="GET", set_session=True, **dict(email=email,))
            club = self.context['club']
            self.assertEqual(club['email'], email)

    @parameterized.expand([
        ("/showSummary", 200, "index.html", "admin@irontemple.com"),
    ])
    def test_show_summary_get_method_no_session(self, url, status_code, template_name, email):
        """
        Test function server.showSummary() with an non valid email
        """
        with self.captured_templates() as templates:
            self.verify_response_template_context(url, status_code,
                                                  template_name, templates,
                                                  method="GET", set_session=False, **dict(email=email,))
            self.assertIn(b"Something went wrong-please try again", self.response.data)

    @parameterized.expand([
        ("She Lifts", "Fall Classic", 200, "booking.html"),
    ])
    def test_book(self, club_name, competition_name, status_code, template_name):
        """
        Test function server.book(competition, club) with existing
        competition and club
        """
        with self.captured_templates() as templates:
            url = f"/book/{competition_name}/{club_name}"
            self.verify_response_template_context(url, status_code,
                                                  template_name, templates)
            club = self.context['club']
            competition = self.context["competition"]
            self.assertEqual(club['name'], club_name)
            self.assertEqual(competition['name'], competition_name)

    @parameterized.expand([
        ("She Lifts", "Fall", 200, "index.html"),
        ("She Lifts", "", 404, None),
        ("Iron", "Spring Festival", 200, "index.html"),
        ("", "Spring Festival", 404, None),
        ("", "", 404, None),
    ])
    def test_book_index_error(self, club_name, competition_name,
                              status_code, template_name):
        """
        Test function server.book(competition, club) with non valid
        competition or/and club
        """
        with self.captured_templates() as templates:
            url = f"/book/{competition_name}/{club_name}"
            self.verify_response_template_context(url, status_code,
                                                  template_name, templates)
            if status_code == 200:
                self.assertRaises(IndexError)
                self.assertIn(b"Something went wrong-please try again", self.response.data)

    @parameterized.expand([
        ("/purchasePlaces", 200, "index.html", "Club does not exist", "Competition does not exist"),
        ("/purchasePlaces", 200, "index.html", "Simply Lift", "Competition does not exist"),
        ("/purchasePlaces", 200, "index.html", "Club does not exist", "Fall Classic"),
        ("/purchasePlaces", 200, "index.html", "", ""),
    ])
    def test_purchase_places_index_error(self, url, status_code,
                                         template_name, club_name,
                                         competition_name):
        """
        Test function server.purchasePlaces() with non valid
        competition or/and club
        """
        with self.captured_templates() as templates:
            data = dict()
            data['club'] = club_name
            data['competition'] = competition_name
            data['places'] = "1"
            self.verify_response_template_context(url, status_code,
                                                  template_name, templates,
                                                  "POST", **data)
            self.assertRaises(IndexError)
            self.assertIn(b"Something went wrong-please try again", self.response.data)

    @parameterized.expand([
        ("/purchasePlaces", 200, "booking.html"),
    ])
    def test_purchase_places_assertion_error(self, url, status_code, template_name):
        """
        Test function server.purchasePlaces() with number of places required greater
        than club's points
        """
        with self.captured_templates() as templates:
            data = dict()
            data['club'] = "Iron Temple"
            data['competition'] = "Fall Classic"
            data['places'] = "5"
            points_before = int(server.get_club_by_name(data['club'])['points'])
            number_of_places_before = int(server.get_competition_by_name(data['competition'])['numberOfPlaces'])
            self.verify_response_template_context(url, status_code,
                                                  template_name, templates,
                                                  "POST", **data)
            self.assertRaises(AssertionError)
            points_after = int(self.context['club']['points'])
            number_of_places_after = int(self.context['competition']['numberOfPlaces'])
            self.assertEqual(points_before, points_after)
            self.assertEqual(number_of_places_before, number_of_places_after)
            self.assertIn(b"Number of places required is greater than club&#39;s points", self.response.data)

    @parameterized.expand([
        ("/purchasePlaces", 200, "welcome.html"),
    ])
    def test_purchase_places(self, url, status_code, template_name):
        """
        Test function server.purchasePlaces() with number of places required less
        than club's points
        """
        with self.captured_templates() as templates:
            data = dict()
            data['club'] = "Iron Temple"
            data['competition'] = "Fall Classic"
            data['places'] = "1"
            points_before = int(server.get_club_by_name(data['club'])['points'])
            number_of_places_before = int(server.get_competition_by_name(data['competition'])['numberOfPlaces'])
            self.verify_response_template_context(url, status_code,
                                                  template_name, templates,
                                                  "POST", **data)
            self.assertRaises(AssertionError)
            points_after = int(self.context['club']['points'])
            number_of_places_after = int(server.get_competition_by_name(data['competition'])['numberOfPlaces'])
            self.assertEqual(points_before - points_after, int(data['places']))
            self.assertEqual(number_of_places_before - number_of_places_after, int(data['places']))
            self.assertIn(b"Great-booking complete!", self.response.data)

    @parameterized.expand([
        ("/logout", 200, "index.html"),
    ])
    def test_logout(self, url, status_code, template_name):
        with self.captured_templates() as templates:
            self.verify_response_template_context(url, status_code,
                                                  template_name, templates)
            self.assertIn(b"You are logged out !", self.response.data)

if __name__ == "__main__":
    unittest.main()
