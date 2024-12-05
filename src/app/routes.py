'''
CS3250 - Software Development Methods and Tools - Fall 2024
Instructor: Thyago Mota
Student(s): Hannah, Amina, Alex, Logan, Patty 
Description: Project 3 - DDR WebSearch


    in progress !!!
'''
from sqlalchemy.sql.expression import func
from app import app, db, cache
from app.forms import *
from app.models import User, Song, Chart
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user
import bcrypt
from misc import needs_chart

@app.route('/')
@app.route('/index')
@app.route('/index.html', methods=['GET'])
def index():
    form = SearchChartForm()
    page = request.args.get('page', default=1, type=int)  
    songName = request.args.get('songName', None, type=str)  
    artist = request.args.get('artist', None, type=str)
    games = request.args.get('games', None)
    difficultyClass = request.args.get("difficultyClass", None)
    higherBPM = request.args.get('higherBPM', None, type=int)
    lowerBPM = request.args.get('lowerBPM', None, type=int)
    maxRuntime = request.args.get("maxRuntime", None, type=int)
    licensed = request.args.get("licensed", default="Don't care")
    changingBPM = request.args.get('changingBPM', default="Don't care")
    maxNotes = request.args.get("maxNotes", None, type=int)
    minNotes = request.args.get("minNotes", None, type=int)
    excludeDoubles = request.args.get("excludeDoubles", default="Include doubles charts")
    shockNotes = request.args.get("shockNotes", default="Include shock charts")
    page_size = 20
    if form.validate_on_submit():
        page = 1
        filters = []
        # First filter by properties innate to the songs
        if form.songName.data :
            filters.append(Song.song_name.like(form.songName.data))
        if form.artist.data : 
            filters.append(Song.artist.like(form.artist.data))
        if form.licensed.data != "Don't care": 
            filters.append(Song.licensed == (form.licensed.data == "Yes"))
        if form.changingBPM.data != "Don't care": 
            filters.append(Song.changing_bpm == (form.changingBPM.data == "Yes"))
        if form.maxRuntime.data :
            filters.append(Song.maxRuntime <= form.maxRuntime.data)
        if form.games.data :
            filters.append(Song.game.any(in_(form.games.data)))
        # Now we query charts, if we have to. 
        if needs_chart(form) :
            pass
    # if filters :
    #     songs = Song.query.filter(and_(*filters)).paginate(page=page, per_page=page_size, error_out=False)
    # else :
    songs = Song.query.paginate(page=page, per_page=page_size, error_out=False)
    return render_template(
        'index.html', 
        songs=songs,
        form=form,
        page=page,
        songName=songName,
        artist=artist,
        game=games, 
        difficultyClass=difficultyClass,
        higherBPM=higherBPM, 
        lowerBPM=lowerBPM,
        maxRuntime=maxRuntime,
        licensed=licensed,
        changingBPM=changingBPM,
        maxNotes=maxNotes,
        minNotes=minNotes,
        excludeDoubles=excludeDoubles,
        shockNotes=shockNotes
    )

@app.route('/users/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        if form.password.data == form.confirm_password.data:
            user_id = form.id.data.strip()
            existing_user = User.query.filter_by(id=user_id).first()
            if existing_user is None:
                hashed_passwd = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
                new_user = User(id=user_id, name=form.name.data, about=form.about.data, admin=False, passwd=hashed_passwd)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('index')) 
            else:
                flash("user ID already taken! please choose a different one.")
        else:
            flash("passwords do not match! please try again.")
    return render_template('signup.html', form=form)

@app.route('/users/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.checkpw(form.password.data.encode("utf-8"), user.password.encode("utf-8")):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            flash('Incorrect email or password. Please try again.')
    return render_template('login.html', form=form)

@login_required
@app.route('/users/signout', methods=['GET', 'POST'])
def signout():
    logout_user()
    flash('you have been logged out.')
    return redirect(url_for('login'))

@app.route('/users/profile')
def profile():
    return 'Work in progress...'

@app.route('/songs') # + song code
def songs():
    return 'Work in progress...'

@app.route('/games') # + game code 
def games():
    return 'Work in progress...'

@app.route('/charts')
def charts():
    return 'Work in progress...'

@app.route('/remove_favorite') # + favorite id
def remove_favorite():
    return 'Work in progress...'

@app.route('/add_favorite') # + song code
def add_favorite():
    return 'Work in progress...'

@app.route('/favorites') 
def favorites():
    return 'Work in progress...'

@app.route('/search')
def search():
    return 'Work in progress...'
