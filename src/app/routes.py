'''
CS3250 - Software Development Methods and Tools - Fall 2024
Instructor: Thyago Mota
Student(s): Hannah, Amina, Alex, Logan, Patty 
Description: Project 3 - DDR WebSearch


    in progress !!!
'''
import bcrypt
from app import app, db, cache
from app.forms import *
from app.models import User, Song, FavoritesList, Playlist, Chart, FavoritesListSong
from datetime import datetime
from misc import needs_chart
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from functools import wraps
from sqlalchemy.sql.expression import func
from sqlalchemy import Table, Column, Integer, String, ForeignKey, and_

@app.route('/')
@app.route('/index')
@app.route('/index.html', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=["GET", "POST"])
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
    filters = []
    if form.validate_on_submit():
        # print("i validated")
        page = 1
        # First filter by properties innate to the songs
        if form.songName.data :
            # print(str(form.songName))
            filters.append(Song.song_name.ilike(f"%{form.songName.data}%"))
        if form.artist.data : 
            filters.append(Song.artist.ilike(f"%{form.artist.data}%"))
        if form.licensed.data != "Don't care": 
            filters.append(Song.licensed == (form.licensed.data == "Yes"))
        if form.changingBPM.data != "Don't care": 
            filters.append(Song.changing_bpm == (form.changingBPM.data == "Yes"))
        if form.maxRuntime.data :
            filters.append(Song.runtime <= form.maxRuntime.data)
        if form.games.data :
            filters.append(Song.game.in_(form.games.data))
        if form.highestDifficulty.data :
            filters.append(Song.charts.any(Chart.difficulty_rating <= form.highestDifficulty.data))
        if form.lowestDifficulty.data :
            filters.append(Song.charts.any(Chart.difficulty_rating >= form.lowestDifficulty.data))\
        
    else : 
        print("form.errors", form.errors)
    songs = []
    print("filters:",filters)
    try: 
        if filters :
            songs = Song.query.filter(and_(*filters)).paginate(page=page, per_page=page_size, error_out=False)
            print("songs:", str(songs.items))
        else :
            songs = Song.query.paginate(page=page, per_page=page_size, error_out=False)
    except Exception as e:
        print(f"Something went wrong querying the database {e}")

    playlists = Playlist.query.filter_by(user_id=current_user.id).all()    
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
        shockNotes=shockNotes,
        playlists=playlists
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
                return redirect(url_for('index')) 
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

@app.route('/users/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('you have been logged out.')
    return redirect(url_for('index'))

class CSRFForm(FlaskForm):
    pass

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    update_name_form = UpdateNameForm()
    update_password_form = UpdatePasswordForm()
    update_email_form = UpdateEmailForm()
    playlist_form = CreatePlaylistForm()
    csrf_form = CSRFForm()

    favorites_list = FavoritesList.query.filter_by(user_id=current_user.id).first()
    if favorites_list:
        favorites = db.session.query(FavoritesListSong, Song).join(Song).filter(
            FavoritesListSong.favorites_list_id == favorites_list.id
        ).all()
    else:
        favorites = []

    playlists = Playlist.query.filter_by(user_id=current_user.id).all()

    section = request.args.get('section', 'default-message')

    if request.method == 'POST':
        if update_name_form.submit_name.data and update_name_form.validate_on_submit():
            current_user.name = update_name_form.name.data
            db.session.commit()
            flash("Name updated successfully!", "success")
            return redirect(url_for('profile', section='default-message'))

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
                return redirect(url_for('profile', section='default-message'))
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
                return redirect(url_for('profile', section='default-message'))

        if playlist_form.submit_playlist.data and playlist_form.validate_on_submit():
            playlist_name = playlist_form.name.data
            new_playlist = Playlist(name=playlist_name, user_id=current_user.id)
            db.session.add(new_playlist)
            db.session.commit()
            flash(f"Playlist '{playlist_name}' created successfully!", "success")
            return redirect(url_for('profile', section='playlists'))

    return render_template(
        'profile.html',
        update_name_form=update_name_form,
        update_password_form=update_password_form,
        update_email_form=update_email_form,
        playlist_form=playlist_form,
        favorites=favorites,
        playlists=playlists,
        section=section,
        form=csrf_form
    )

def admin_required(f):
    @wraps(f)
    def wrap_decorator_function_admin(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page', 'error')
            return redirect(url_for('admin_error'))
        return f(*args, **kwargs)
    return wrap_decorator_function_admin


@app.route('/song/<int:song_id>', methods=['GET', 'POST'])
@admin_required
@login_required
def edit_song(song_id):
    song = Song.query.get_or_404(song_id)
    print(f"Initializing edit_song route for Song ID: {song_id}, Song Name: {song.song_name}")

    form = EditSongForm(song=song)

    if form.validate_on_submit():
        print("Form submitted data:", form.data)

        print(f"Updating Song Name from {song.song_name} to {form.songName.data}")
        song.song_name = form.songName.data
        song.artist = form.artist.data
        song.higher_bpm = form.higherBPM.data
        song.lower_bpm = form.lowerBPM.data
        song.runtime = form.runtime.data
        song.licensed = form.licensed.data
        song.game = form.game.data

        for i, chart_form in enumerate(form.charts.entries):
            if i < len(song.charts):
                chart = song.charts[i]
                print(f"Updating Chart ID {chart.id} with new values.")
                chart.difficulty = chart_form.difficulty.data
                chart.is_doubles = chart_form.isDoubles.data
                chart.notes = chart_form.notes.data or 0
                chart.freeze_notes = chart_form.freezeNotes.data or 0
                chart.shock_notes = chart_form.shockNotes.data or 0
                chart.difficulty_rating = chart_form.difficultyRating.data or 0

        db.session.commit()
        updated_song = Song.query.get(song_id)
        print(f"Post-commit DB check: Song Name: {updated_song.song_name}, Artist: {updated_song.artist}")

        flash("Song updated successfully!", "success")
        return redirect(url_for("search"))

    if request.method == "POST":
        print("Form validation errors:", form.errors)

    return render_template("edit_song.html", form=form, song=song)

@app.route('/songs/<int:id>/delete')
@admin_required
@login_required
def delete_song(id):
    song = db.session.query(Song).get(id)
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for('songs'))

@app.route('/add_song', methods=['GET', 'POST'])
@admin_required
@login_required
def add_song():
    song_form = AddSongForm()

    if request.method == 'POST':

        if song_form.validate_on_submit():
            try:

                new_song = Song(
                    song_name=song_form.songName.data,
                    artist=song_form.artist.data,
                    higher_bpm=song_form.higherBPM.data,
                    lower_bpm=song_form.lowerBPM.data,
                    licensed=song_form.licensed.data,
                    changing_bpm=song_form.changingBPM,
                    runtime=song_form.runtime.data,
                    game=song_form.game.data
                )
                db.session.add(new_song)
                db.session.commit()


                for chart_form in song_form.charts.entries:
                    new_chart = Chart(
                        song_id=new_song.id,
                        difficulty=chart_form.form.difficulty.data,
                        is_doubles=chart_form.form.isDoubles.data,
                        notes=chart_form.form.notes.data,
                        freeze_notes=chart_form.form.freezeNotes.data,
                        shock_notes=chart_form.form.shockNotes.data,
                        difficulty_rating=chart_form.form.difficultyRating.data
                    )
                    db.session.add(new_chart)
                db.session.commit()

                flash(f"Song '{new_song.song_name}' added successfully!", "success")
                return redirect(url_for('index'))

            except Exception as e:
                db.session.rollback()  
                print("Database error:", str(e))
                flash("An error occurred while adding the song. Please try again.", "danger")
        else:
            print("Form validation errors:", song_form.errors)
            flash("There were errors in your form submission. Please check your inputs.", "danger")

    return render_template('add_song.html', song_form=song_form)

@app.route('/remove_favorite/<int:favorites_list_id>/<int:song_id>', methods=['POST'])
@login_required
def remove_favorite(favorites_list_id, song_id):
    favorite = FavoritesListSong.query.filter_by(
        favorites_list_id=favorites_list_id,
        song_id=song_id
    ).first_or_404()
    
    favorites_list = FavoritesList.query.get_or_404(favorites_list_id)
    if favorites_list.user_id != current_user.id:
        flash('Unauthorized action!', 'error')
        return redirect(url_for('profile', section='favorites'))

    db.session.delete(favorite)
    db.session.commit()
    flash('Song removed from favorites.', 'success')
    return redirect(url_for('profile', section='favorites'))

@app.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    try:
        song_id = request.form.get('song_id')
        song = Song.query.get(song_id)

        if not song:
            flash("Song not found.", "danger")
            return redirect(url_for('profile', section='favorites'))

        favorite_list = FavoritesList.query.filter_by(user_id=current_user.id).first()

        if not favorite_list:
            favorite_list = FavoritesList(user_id=current_user.id)
            db.session.add(favorite_list)
            db.session.commit()

        existing_favorite = FavoritesListSong.query.filter_by(
            favorites_list_id=favorite_list.id,
            song_id=song_id
        ).first()

        if existing_favorite:
            flash("This song is already in your favorites.", "info")
        else:
            new_favorite = FavoritesListSong(favorites_list_id=favorite_list.id, song_id=song_id)
            db.session.add(new_favorite)
            db.session.commit()
            flash(f"{song.song_name} has been added to your favorites!", "success")

        return redirect(url_for('profile', section='favorites'))

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('profile', section='favorites'))

@app.route('/favorites', methods=['GET'])
@login_required
def view_favorites():
    favorites_list = FavoritesList.query.filter_by(user_id=current_user.id).first()

    if not favorites_list or favorites_list.songs.count() == 0:
        flash('You have no favorite songs.', 'info')
        return render_template('favorites.html', favorites=[])

    return render_template('favorites.html', favorites=favorites_list.songs)

@app.route('/add_song_to_playlist', methods=['POST'])
@login_required
def add_song_to_playlist():
    playlist_id = request.form.get('playlist_id')
    song_id = request.form.get('song_id')

    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
    if not playlist:
        flash("Playlist not found!", "danger")
        return redirect(url_for('profile', section='playlists'))

    song = Song.query.get(song_id)
    if not song:
        flash("Song not found!", "danger")
        return redirect(url_for('profile', section='playlists'))

    if song in playlist.songs:
        flash("Song is already in this playlist!", "info")
    else:
        playlist.songs.append(song)
        db.session.commit()
        flash(f"Song added to playlist '{playlist.name}'!", "success")

    return redirect(url_for('profile', section='playlists'))

@app.route('/admin_error')
def admin_error():
    return render_template('admin_error.html'), 403