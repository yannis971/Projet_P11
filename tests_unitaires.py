import unittest
from contextlib import contextmanager
from flask import template_rendered
from parameterized import parameterized
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

    def test_get_club_by_name(self):
        club = server.get_club_by_name("Simply Lift")
        self.assertEqual(club['name'], "Simply Lift")

    def test_get_competition_by_name(self):
        competition = server.get_competition_by_name("Spring Festival")
        self.assertEqual(competition['name'], "Spring Festival")

    def test_index(self):
        with self.captured_templates() as templates:
            response = self.app.test_client().get('/', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'index.html')

    @parameterized.expand([
        ("john.doe@gmail.com", 200, b"Sorry, that email john.doe@gmail.com was not found."),
        ("", 200, b"Sorry, that email  was not found."),
    ])
    def test_show_summary_index_error(self, email, status_code, message):
        with self.captured_templates() as templates:
            response = self.app.test_client().post('/showSummary', data=dict(email=email,), follow_redirects=True)
            self.assertRaises(IndexError)
            self.assertEqual(response.status_code, status_code)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'welcome.html')
            self.assertIn(message, response.data)

    @parameterized.expand([
        ("admin@irontemple.com", 200),
    ])
    def test_show_summary(self, email, status_code):
        with self.captured_templates() as templates:
            response = self.app.test_client().post('/showSummary', data=dict(email=email,), follow_redirects=True)
            self.assertEqual(response.status_code, status_code)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'welcome.html')
            club = context['club']
            self.assertEqual(club['email'], email)

    @parameterized.expand([
        ("She Lifts", "Fall Classic 2021"),
    ])
    def test_book(self, club_name, competition_name):
        with self.captured_templates() as templates:
            response = self.app.test_client().get(f"/book/{competition_name}/{club_name}", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'booking.html')
            club = context['club']
            competition = context["competition"]
            self.assertEqual(club['name'], club_name)
            self.assertEqual(competition['name'], competition_name)

    @parameterized.expand([
        ("She Lifts", "Fall", 200),
        ("She Lifts", "", 404),
        ("Iron", "Spring Festival", 200),
        ("", "Spring Festival", 404),
        ("", "", 404),
    ])
    def test_book_index_error(self, club_name, competition_name, status_code):
        with self.captured_templates() as templates:
            response = self.app.test_client().get(f"/book/{competition_name}/{club_name}", follow_redirects=True)
            self.assertRaises(IndexError)
            self.assertEqual(response.status_code, status_code)
            if status_code == 200:
                self.assertEqual(len(templates), 1)
                template, context = templates[0]
                self.assertEqual(template.name, 'welcome.html')
                self.assertIn(b"Something went wrong-please try again", response.data)

    @parameterized.expand([
        ("She Lifts", "Fall Classic"),
        ("Iron Temple", "Spring Festival"),
    ])
    def test_book_past_competition(self, club_name, competition_name):
        with self.captured_templates() as templates:
            response = self.app.test_client().get(f"/book/{competition_name}/{club_name}", follow_redirects=True)
            self.assertRaises(AssertionError)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'welcome.html')
            self.assertIn(b"Competition is no longer valid", response.data)

    @parameterized.expand([
        ("She Lifts", "Date Error 01"),
        ("She Lifts", "Date Error 02"),
    ])
    def test_book_value_error(self, club_name, competition_name):
        with self.captured_templates() as templates:
            response = self.app.test_client().get(f"/book/{competition_name}/{club_name}", follow_redirects=True)
            self.assertRaises(ValueError)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'welcome.html')
            self.assertIn(b"Something went wrong :", response.data)

    def test_purchase_places_index_error(self, **dico):
        with self.captured_templates() as templates:
            dico = dict()
            dico['club'] = "Club does not exist"
            dico['competition'] = "Competition does not exist"
            dico['places'] = "1"
            response = self.app.test_client().post("/purchasePlaces", data=dico, follow_redirects=True)
            self.assertRaises(IndexError)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'welcome.html')
            self.assertIn(b"Something went wrong-please try again", response.data)

    def test_purchase_places_assertion_error(self):
        with self.captured_templates() as templates:
            dico = dict()
            dico['club'] = "Iron Temple"
            dico['competition'] = "Fall Classic"
            dico['places'] = "5"
            points_before = int(server.get_club_by_name(dico['club'])['points'])
            number_of_places_before = int(server.get_competition_by_name(dico['competition'])['numberOfPlaces'])
            response = self.app.test_client().post("/purchasePlaces", data=dico, follow_redirects=True)
            self.assertRaises(AssertionError)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            points_after = int(context['club']['points'])
            number_of_places_after = int(context['competition']['numberOfPlaces'])
            self.assertEqual(points_before, points_after)
            self.assertEqual(number_of_places_before, number_of_places_after)
            self.assertEqual(template.name, 'booking.html')
            self.assertIn(b"Number of places required is greater than club&#39;s points", response.data)

    def test_purchase_more_than_max_places(self):
        with self.captured_templates() as templates:
            dico = dict()
            dico['club'] = "Simply Lift"
            dico['competition'] = "Spring Festival"
            dico['places'] = "13"
            points_before = int(server.get_club_by_name(dico['club'])['points'])
            number_of_places_before = int(server.get_competition_by_name(dico['competition'])['numberOfPlaces'])
            response = self.app.test_client().post("/purchasePlaces", data=dico, follow_redirects=True)
            self.assertRaises(AssertionError)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            points_after = int(context['club']['points'])
            number_of_places_after = int(context['competition']['numberOfPlaces'])
            self.assertEqual(points_before, points_after)
            self.assertEqual(number_of_places_before, number_of_places_after)
            self.assertEqual(template.name, 'booking.html')
            self.assertIn(b"Number of places required is greater than 12", response.data)

    def test_purchase_places(self):
        with self.captured_templates() as templates:
            dico = dict()
            dico['club'] = "Iron Temple"
            dico['competition'] = "Fall Classic"
            dico['places'] = "1"
            points_before = int(server.get_club_by_name(dico['club'])['points'])
            number_of_places_before = int(server.get_competition_by_name(dico['competition'])['numberOfPlaces'])
            response = self.app.test_client().post("/purchasePlaces", data=dico, follow_redirects=True)
            self.assertRaises(AssertionError)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            points_after = int(context['club']['points'])
            number_of_places_after = int(server.get_competition_by_name(dico['competition'])['numberOfPlaces'])
            self.assertEqual(points_before - points_after, int(dico['places']))
            self.assertEqual(number_of_places_before - number_of_places_after, int(dico['places']))
            self.assertEqual(template.name, 'welcome.html')
            self.assertIn(b"Great-booking complete!", response.data)


if __name__ == "__main__":
    unittest.main()