import os
import json
from flask import Flask, flash, render_template, request, redirect, session, url_for


app = Flask(__name__)
app.config.from_object('config')


def loadClubs():
    with open(os.path.join(app.config['BASE_DIR'], os.path.dirname(__file__), 'clubs.json')) as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open(os.path.join(app.config['BASE_DIR'], os.path.dirname(__file__), 'competitions.json')) as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


competitions = loadCompetitions()
clubs = loadClubs()


def get_club_by_name(name):
    return [c for c in clubs if c['name'] == name][0]


def get_competition_by_name(name):
    return [c for c in competitions if c['name'] == name][0]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['GET', 'POST'])
def showSummary():
    if request.method == "POST":
        session['email'] = request.form['email']
    if request.method == "GET" and 'email' not in session:
        flash("Something went wrong-please try again", category='error')
        return redirect(url_for('index'))
    try:
        club = [club for club in clubs if club['email'] == session['email']][0]
    except IndexError:
        flash(f"Sorry, that email {request.form['email']} was not found.", category='error')
        return redirect(url_for('index'))
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    try:
        foundClub = get_club_by_name(club)
        foundCompetition = get_competition_by_name(competition)
    except IndexError:
        flash("Something went wrong-please try again", category='error')
        return redirect(url_for('index'))
    else:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    try:
        competition = get_competition_by_name(request.form['competition'])
        club = get_club_by_name(request.form['club'])
        places_required = int(request.form['places'])
        points_allowed = int(club['points'])
        assert points_allowed >= places_required
    except IndexError:
        flash("Something went wrong-please try again", category='error')
        return redirect(url_for('index'))
    except AssertionError:
        flash("Number of places required is greater than club's points", category='error')
        return render_template('booking.html', club=club, competition=competition)
    else:
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - places_required
        club['points'] = int(club['points']) - places_required
        flash('Great-booking complete!')
        return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You are logged out !')
    return redirect(url_for('index'))
