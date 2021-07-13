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
        ("/logout", 200, "index.html"),
    ])
    def test_logout(self, url, status_code, template_name):
        """
        Test function server.logout
        """
        with self.captured_templates() as templates:
            self.verify_response_template_context(url, status_code,
                                                  template_name, templates)
            self.assertIn(b"You are logged out !", self.response.data)


if __name__ == "__main__":
    unittest.main()
