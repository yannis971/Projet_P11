import json
from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

MAX_BOOKING_PLACES = 12


def get_club_by_name(name):
    return [c for c in clubs if c['name'] == name][0]


def get_competition_by_name(name):
    return [c for c in competitions if c['name'] == name][0]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    try:
        club = [club for club in clubs if club['email'] == request.form['email']][0]
    except IndexError:
        flash(f"Sorry, that email {request.form['email']} was not found.")
        club = {"name": "", "email": "", "points": ""}
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    try:
        foundClub = get_club_by_name(club)
        foundCompetition = get_competition_by_name(competition)
    except IndexError:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)
    else:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    try:
        competition = get_competition_by_name(request.form['competition'])
        club = get_club_by_name(request.form['club'])
        places_required = int(request.form['places'])
        points_allowed = int(club['points'])
        assert points_allowed >= places_required, "Number of places required is greater than club's points"
        assert MAX_BOOKING_PLACES >= places_required, f"Number of places required is greater than {MAX_BOOKING_PLACES}"
    except IndexError:
        flash("Something went wrong-please try again")
        club = {"name": request.form['club'], "email": "", "points": ""}
        return render_template('welcome.html', club=club, competitions=competitions)
    except AssertionError as assertion_error:
        flash(assertion_error)
        return render_template('booking.html', club=club, competition=competition)
    else:
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - places_required
        club['points'] = int(club['points']) - places_required
        flash('Great-booking complete!')
        return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
