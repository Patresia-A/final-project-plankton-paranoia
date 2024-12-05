'''
CS3250 - Software Development Methods and Tools - Fall 2024
Instructor: Thyago Mota
Student(s): Hannah, Amina, Alex, Logan, Patty 
Description: Project 3 - DDR WebSearch


    in progress !!!
'''
from app import app, db, cache
from app.forms import *
from app.models import User
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user
import bcrypt

@app.route('/')
@app.route('/index')
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    form = SearchChartForm()
    page = request.args.get('page', default=1, type=int)  
    songName = request.args.get('songName', None)  
    artist = request.args.get('artist', None)
    games = request.args.get('games', None)
    higherBPM = request.args.get('higherBPM', None)
    lowerBPM = request.args.get('lowerBPM', None)
    runtime = request.args.get("runtime", None)
    licensed = request.args.get("licensed", None),
    changingBPM = request.args.get('changingBPM', None)
    if form.validate_on_submit():
        page = 1
    

    return render_template(
        'index.html', 
        songs=[],
        form=form,
        page = page
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

@app.route('/songs/<int:id>/delete')
def delete_song(id):
    song = db.session.query(Song).get(id)
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for('songs'))

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
