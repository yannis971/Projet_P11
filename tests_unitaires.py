import unittest
from contextlib import contextmanager
from flask import template_rendered
import server


class ServerUnitTests(unittest.TestCase):

    def setUp(self) -> None:
        self.app = server.app
        self.app.config['TESTING'] = True
        self.app.config['DEBUG'] = False

    def tearDown(self) -> None:
        pass

    @contextmanager
    def captured_templates(self):
        recorded = []

        def record(sender, template, context, **extra):
            recorded.append((template, context))

        template_rendered.connect(record, self.app)
        try:
            yield recorded
        finally:
            template_rendered.disconnect(record, self.app)

    def test_load_clubs(self):
        load_clubs = server.loadClubs()
        self.assertIsInstance(load_clubs, list)
        for club in load_clubs:
            for key in ('name', 'email', 'points'):
                self.assertTrue(key in club)

    def test_load_competitions(self):
        load_competitions = server.loadCompetitions()
        self.assertIsInstance(load_competitions, list)
        for competition in load_competitions:
            for key in ('name', 'date', 'numberOfPlaces'):
                self.assertTrue(key in competition)

    def test_index(self):
        with self.captured_templates() as templates:
            response = self.app.test_client().get('/', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'index.html')

    def test_show_summary_index_error(self):
        with self.captured_templates() as templates:
            email = "john.doe@gmail.com"
            response = self.app.test_client().post('/showSummary', data=dict(email=email,), follow_redirects=True)
            self.assertRaises(IndexError)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'welcome.html')
            self.assertIn(b"Sorry, that email john.doe@gmail.com was not found.", response.data)

    def test_show_summary(self):
        with self.captured_templates() as templates:
            email = "admin@irontemple.com"
            response = self.app.test_client().post('/showSummary', data=dict(email=email,), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'welcome.html')
            club = context['club']
            self.assertEqual(club['email'], email)


if __name__ == "__main__":
    unittest.main()