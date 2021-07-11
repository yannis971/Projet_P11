
from locust import HttpUser, between, task

# from webapp import server


class SoftDeskPerf(HttpUser):
    wait_time = between(0.5, 5.0)

    @task
    def perf_index(self):
        self.client.get("/")

    @task
    def perf_showSummary(self):
        self.client.post("/showSummary", data={"email": "admin@irontemple.com" })

    @task
    def perf_book(self):
        competition = "Spring Festival"
        club = "Simply Lift"
        self.client.get(f"/book/{competition}/{club}")

    @task
    def perf_purchasePlaces(self):
        competition = "Spring Festival"
        club = "Simply Lift"
        places = "3"
        self.client.post("/purchasePlaces", data={"competition": competition, "club": club, "places": places })

    @task
    def perf_logout(self):
        self.client.get("/logout")