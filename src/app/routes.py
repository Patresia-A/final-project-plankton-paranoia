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
from app.models import User, Song, FavoritesList, Chart
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
import bcrypt
from misc import needs_chart
from functools import wraps

@app.route('/')
@app.route('/index')
@app.route('/index.html', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search')
def search():
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
        'search.html', 
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
            user_email = form.email.data.strip()
            existing_email = User.query.filter_by(email=user_email).first()
            if existing_email is None:
                hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
                new_user = User(name=form.name.data, email=form.email.data, password=hashed_password.decode('utf-8'), role=False)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('login')) 
            else:
                flash("Email is already in use! Please provide a different one.")
        else:
            flash("Passwords do not match! Please try again.")
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
@app.route('/users/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('you have been logged out.')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    update_name_form = UpdateNameForm()
    update_password_form = UpdatePasswordForm()
    update_email_form = UpdateEmailForm()
    playlist_form = CreatePlaylistForm()

    if request.method == 'POST':
        if update_name_form.submit_name.data and update_name_form.validate_on_submit():
            current_user.name = update_name_form.name.data
            db.session.commit()
            flash("Name updated successfully!", "success")
            return redirect(url_for('profile'))

    if update_password_form.submit_password.data and update_password_form.validate_on_submit():
        if bcrypt.checkpw(
            update_password_form.current_password.data.encode('utf-8'),
            current_user.password.encode('utf-8')
        ):
            hashed_password = bcrypt.hashpw(
                update_password_form.new_password.data.encode('utf-8'), bcrypt.gensalt()
            ).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash("Password updated successfully!", "success")
            return redirect(url_for('profile'))
        else:
            flash("Current password is incorrect. Please try again.", "danger")

    if update_email_form.submit_email.data and update_email_form.validate_on_submit():
        existing_user = User.query.filter_by(email=update_email_form.new_email.data).first()
        if existing_user:
            flash("This email is already in use. Please choose a different email.", "danger")
        else:
            current_user.email = update_email_form.new_email.data
            try:
                db.session.commit()
                flash("Email updated successfully!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred while updating the email: {str(e)}", "danger")
            return redirect(url_for('profile'))

    if playlist_form.submit_playlist.data and playlist_form.validate_on_submit():
        new_playlist = FavoritesList(
            name=playlist_form.name.data,
            user_id=current_user.id
        )
        db.session.add(new_playlist)
        db.session.commit()
        flash("Playlist created successfully!", "success")
        return redirect(url_for('profile'))

    playlists = FavoritesList.query.filter_by(user_id=current_user.id).all()
    return render_template(
        'profile.html',
        update_name_form=update_name_form,
        update_password_form=update_password_form,
        update_email_form=update_email_form,
        playlist_form=playlist_form,
        playlists=playlists
    )

@app.route('/songs') # + song code
def songs():
    return 'Work in progress...'

def admin_required(f):
    @wraps(f)
    def wrap_decorator_function_admin(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin:
            flash('You do not have permission to access this page', 'Error!')
            return redirect(url_for('admin_error'))
        return f(*args, **kwargs)
    return wrap_decorator_function_admin

@app.route('/songs/<int:id>/delete')
@admin_required
@login_required
def delete_song(id):
    song = db.session.query(Song).get(id)
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for('songs'))

@app.route('/add_song') # + song code
def add_song():
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
