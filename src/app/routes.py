'''
CS3250 - Software Development Methods and Tools - Fall 2024
Instructor: Thyago Mota
Student(s): Hannah, Amina, Alex, Logan, Patty
Description: Project 3 - DDR WebSearch


    in progress !!!
'''
import bcrypt
from app import app
from app.extensions import db, cache
from app.forms import *
from app.models import User, Song, FavoritesList, Playlist, Chart, FavoritesListSong
from datetime import datetime
from misc import needs_chart
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
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
    def array_to_comma_string(strings):
        print("strings: ", strings)
        if strings:
            return ",".join(strings)
        return None
    form = SearchChartForm()
    page = request.args.get('page', default=1, type=int)
    songName = request.args.get('songName', default=None, type=str)
    artist = request.args.get('artist', default=None, type=str)
    highestDifficulty = request.args.get(
        "highestDifficulty", default=None, type=str
    )
    lowestDifficulty = request.args.get(
        "lowestDifficulty",
        default=None,
        type=str
    )
    games = request.args.get('games', default=None)
    games_arr = games.split(",") if games else None
    difficultyClass = request.args.get("difficultyClass", default=None)
    difficultyClass_arr = (
        difficultyClass.split(",") if difficultyClass else None
    )
    higherBPM = request.args.get('higherBPM', default=None, type=int)
    lowerBPM = request.args.get('lowerBPM', default=None, type=int)
    maxRuntime = request.args.get("maxRuntime", default=None, type=int)
    licensed = request.args.get("licensed", default="Don't care")
    changingBPM = request.args.get('changingBPM', default="Don't care")
    maxNotes = request.args.get("maxNotes", default=None, type=int)
    minNotes = request.args.get("minNotes", default=None, type=int)
    excludeDoubles = request.args.get(
        "excludeDoubles",
        default="Include doubles charts"
    )
    shockNotes = request.args.get("shockNotes", default="Include shock charts")
    page_size = 20
    filters = []
    chartFilters = []
    # case where we are making a new query
    if form.validate_on_submit():
        page = 1
        # First filter by properties innate to the songs
        if form.songName.data:
            songName = form.songName.data
            filters.append(Song.song_name.ilike(f"%{songName}%"))
        if form.artist.data:
            artist = form.artist.data
            filters.append(Song.artist.ilike(f"%{artist}%"))
        if form.licensed.data != "Don't care":
            licensed = form.licensed.data
            filters.append(Song.licensed == (licensed == "Yes"))
        if form.changingBPM.data != "Don't care":
            changingBPM = form.changingBPM.data
            filters.append(Song.changing_bpm == (changingBPM == "Yes"))
        if form.maxRuntime.data:
            maxRuntime = form.maxRuntime.data
            filters.append(Song.runtime <= maxRuntime)
        if form.games.data:
            games_arr = form.games.data
            games = array_to_comma_string(games_arr)
            filters.append(Song.game.in_(games_arr))
        if form.higherBPM.data:
            higherBPM = form.higherBPM.data
            filters.append(Song.higher_bpm <= higherBPM)
        if form.lowerBPM.data:
            lowerBPM = form.lowerBPM.data
            filters.append(Song.lower_bpm >= lowerBPM)
        # now for all the chart filters...
        if form.highestDifficulty.data:
            highestDifficulty = form.highestDifficulty.data
            chartFilters.append(Chart.difficulty_rating <= highestDifficulty)
        if form.lowestDifficulty.data:
            lowestDifficulty = form.lowestDifficulty.data
            chartFilters.append(Chart.difficulty_rating >= lowestDifficulty)
        if form.difficultyClass.data:
            difficultyClass_arr = form.difficultyClass.data
            print(form.difficultyClass.data)
            difficultyClass = array_to_comma_string(difficultyClass_arr)
            chartFilters.append(Chart.difficulty.in_(difficultyClass_arr))
        if form.maxNotes.data:
            maxNotes = form.maxNotes.data
            chartFilters.append(Chart.notes <= maxNotes)
        if form.minNotes.data:
            minNotes = form.minNotes.data
            chartFilters.append(Chart.notes >= minNotes)
        if form.excludeDoubles.data != "Include doubles charts":
            excludeDoubles = form.excludeDoubles.data
            chartFilters.append(Chart.is_doubles == (
                excludeDoubles == "Include only doubles charts")
            )   # otherwise we only want singles charts
        if form.shockNotes.data != "Include shock charts":
            shockNotes = form.shockNotes.data
        if shockNotes == "Exclude shock charts":
            chartFilters.append(Chart.shock_notes == 0)
        elif shockNotes == "Include only shock charts":
            chartFilters.append(Chart.shock_notes != 0)

    # redirected or paginated case...
    else:
        print("dclass", difficultyClass)
        if songName:
            filters.append(Song.song_name.ilike(f"%{songName}%"))
        if artist:
            filters.append(Song.song_name.ilike(f"%{artist}%"))
        if licensed:
            filters.append(Song.licensed == (licensed == "Yes"))
        if changingBPM != "Don't care":
            filters.append(Song.changing_bpm == (changingBPM == "Yes"))
        if maxRuntime:
            filters.append(Song.runtime <= maxRuntime)
        if games:
            print("games!")
            filters.append(Song.game.in_(games_arr))
        if higherBPM:
            filters.append(Song.higher_bpm <= higherBPM)
        if lowerBPM:
            filters.append(Song.lower_bpm >= lowerBPM)
        # Now for chart filters
        if highestDifficulty:
            chartFilters.append(Chart.difficulty_rating <= highestDifficulty)
        if lowestDifficulty:
            chartFilters.append(Chart.difficulty_rating >= lowestDifficulty)
        if difficultyClass:
            print("Difficulty:", difficultyClass_arr)
            chartFilters.append(Chart.difficulty.in_(difficultyClass_arr))
        if maxNotes:
            chartFilters.append(Chart.notes <= maxNotes)
        if minNotes:
            chartFilters.append(Chart.notes >= minNotes)
        if excludeDoubles != "Include doubles charts":
            chartFilters.append(
                Chart.is_doubles == (
                    excludeDoubles == "Include only doubles charts")
            )  # otherwise we only want singles charts
        if shockNotes != "Include shock charts":
            if shockNotes == "Exclude shock charts":
                chartFilters.append(Chart.shock_notes == 0)
            elif shockNotes == "Include only shock charts":
                chartFilters.append(Chart.shock_notes != 0)

    songs = []
    try:
        if filters:
            songs = Song.query.filter(and_(*filters)).paginate(
                page=page,
                per_page=page_size,
                error_out=False
            )
            print("songs:", str(songs.items))
        else:
            songs = Song.query.paginate(
                page=page,
                per_page=page_size,
                error_out=False
            )
    except Exception as e:
        print(f"Something went wrong querying the database {e}")
    return render_template(
        'search.html',
        songs=songs,
        form=form,
        page=page,
        songName=songName,
        artist=artist,
        games=games,
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
                hashed_password = bcrypt.hashpw(
                    form.password.data.encode('utf-8'), bcrypt.gensalt())
                new_user = User(
                    name=form.name.data,
                    email=form.email.data,
                    password=hashed_password.decode('utf-8'),
                    role=False
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('index'))
            else:
                flash(
                    "Email is already in use! Please provide a different one."
                )
        else:
            flash("Passwords do not match! Please try again.")
    return render_template('signup.html', form=form)


@app.route('/users/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.checkpw(
                form.password.data.encode("utf-8"),
                user.password.encode("utf-8")):
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


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    update_name_form = UpdateNameForm()
    update_password_form = UpdatePasswordForm()
    update_email_form = UpdateEmailForm()
    playlist_form = CreatePlaylistForm()

    favorites_list = FavoritesList.query.filter_by(
        user_id=current_user.id).first()
    favorites = favorites_list.songs if favorites_list else []

    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    db.session.refresh(current_user)
    print("Playlists:", playlists)

    if request.method == 'POST':
        if (update_name_form.submit_name.data
                and update_name_form.validate_on_submit()):
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
                update_password_form.new_password.data.encode(
                    'utf-8'), bcrypt.gensalt()
            ).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash("Password updated successfully!", "success")
            return redirect(url_for('profile'))
        else:
            flash("Current password is incorrect. Please try again.", "danger")

    if update_email_form.submit_email.data and update_email_form.validate_on_submit():
        existing_user = User.query.filter_by(
            email=update_email_form.new_email.data).first()
        if existing_user:
            flash(
                "This email is already in use. Please choose a different email.", "danger")
        else:
            current_user.email = update_email_form.new_email.data
            try:
                db.session.commit()
                flash("Email updated successfully!", "success")
            except Exception as e:
                db.session.rollback()
                flash(
                    f"An error occurred while updating the email: {str(e)}", "danger")
            return redirect(url_for('profile'))

    if playlist_form.validate_on_submit():
        playlist_name = playlist_form.name.data
        new_playlist = Playlist(name=playlist_name, user_id=current_user.id)
        db.session.add(new_playlist)
        db.session.commit()

        playlist_table_name = f"playlist_{new_playlist.id}"
        playlist_table = Table(
            playlist_table_name,
            db.metadata,
            Column('id', Integer, primary_key=True),
            Column('song_id', Integer, ForeignKey('songs.id')),
            Column('added_date', String, nullable=False)
        )
        db.metadata.create_all(db.engine)

        flash(f"Playlist '{playlist_name}' created successfully!", "success")
        return redirect(url_for('profile'))

    playlists = FavoritesList.query.filter_by(user_id=current_user.id).all()
    return render_template(
        'profile.html',
        update_name_form=update_name_form,
        update_password_form=update_password_form,
        update_email_form=update_email_form,
        playlist_form=playlist_form,
        favorites=favorites,
        playlists=playlists
    )


@app.route('/songs')  # + song code
def songs():
    return 'Work in progress...'


@app.route('/games')  # + game code
def games():
    return 'Work in progress...'


@app.route('/charts')
def charts():
    return 'Work in progress...'


def admin_required(f):
    @wraps(f)
    def wrap_decorator_function_admin(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page', 'error')
            return redirect(url_for('admin_error'))
        return f(*args, **kwargs)
    return wrap_decorator_function_admin


@app.route('/song/<string:song_name>', methods=['GET', 'POST'])
@admin_required
@login_required
def edit_song(song_name):
    song = Song.query.filter_by(song_name=song_name).first_or_404()
    form = EditSongForm(song=song)

    if form.validate_on_submit():
        song.song_name = form.songName.data
        song.artist = form.artist.data
        song.higher_bpm = form.higherBPM.data
        song.lower_bpm = form.lowerBPM.data
        song.runtime = form.runtime.data
        song.licensed = form.licensed.data
        song.game = form.game.data

        for chart_form, chart in zip(form.charts, song.charts):
            chart.difficulty = chart_form.difficulty.data
            chart.is_doubles = chart_form.isDoubles.data
            chart.notes = chart_form.notes.data
            chart.freeze_notes = chart_form.freezeNotes.data
            chart.shock_notes = chart_form.shockNotes.data
            chart.difficulty_rating = chart_form.difficultyRating.data

        db.session.commit()
        flash('Song updated successfully!', 'success')
        return redirect(url_for('search'))

    return render_template('edit_song.html', form=form, song=song)


@app.route('/songs/<int:id>/delete')
@admin_required
@login_required
def delete_song(id):
    song = db.session.query(Song).get_or_404(id)
    db.session.delete(song)
    db.session.commit()
    flash("Song deleted successfully!", "success")
    return redirect(url_for('search'))


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

                flash(f"Song '{new_song.song_name}' added!", "success")
                return redirect(url_for('index'))

            except Exception as e:
                db.session.rollback()
                print("Database error:", str(e))
                flash(
                    "Error adding song. Try again.", "danger")
        else:
            print("Form validation errors:", song_form.errors)
            flash(
                "Errors in your form submission. Check your inputs.", "danger"
            )

    return render_template('add_song.html', song_form=song_form)


@app.route('/remove_favorite')  # + favorite id
@login_required
def remove_favorite(favorite_id):
    favorite = FavoritesList.query.get_or_404(favorite_id)
    if favorite.user_id != current_user.id:
        flash('Unauthorized action!', 'error')
        return redirect(url_for('profile'))
    db.session.delete(favorite)
    db.session.commit()
    flash('Song removed from favorites.', 'success')
    return redirect(url_for('view_favorites'))


@app.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    song_id = request.form.get('song_id')
    if not song_id:
        flash('Song ID is required!', 'error')
        return redirect(url_for('profile'))

    song = Song.query.get(song_id)
    if not song:
        flash('Song not found!', 'error')
        return redirect(url_for('profile'))

    favorites_list = FavoritesList.query.filter_by(
        user_id=current_user.id).first()
    if not favorites_list:
        favorites_list = FavoritesList(user_id=current_user.id)
        db.session.add(favorites_list)
        db.session.commit()

    if song in favorites_list.songs:
        flash('Song is already in your favorites!', 'info')
    else:
        favorites_list.songs.append(song)
        db.session.commit()
        flash('Song added to favorites!', 'success')

    return redirect(url_for('profile'))


@app.route('/favorites', methods=['GET'])
@login_required
def view_favorites():
    favorites_list = FavoritesList.query.filter_by(
        user_id=current_user.id).first()

    if not favorites_list or favorites_list.songs.count() == 0:
        flash('You have no favorite songs.', 'info')
        return render_template('favorites.html', favorites=[])

    return render_template('favorites.html', favorites=favorites_list.songs)


@app.route('/add_song_to_playlist/<string:playlist_name>', methods=['POST'])
@login_required
def add_song_to_playlist(playlist_name):
    playlist = Playlist.query.filter_by(
        name=playlist_name, user_id=current_user.id).first()
    if not playlist:
        flash("Playlist not found!", "danger")
        return redirect(url_for('profile'))

    song_id = request.form.get('song_id')
    playlist_table_name = f"playlist_{playlist.id}"

    playlist_table = Table(
        playlist_table_name,
        db.metadata,
        autoload_with=db.engine
    )

    insert_statement = playlist_table.insert().values(
        song_id=song_id, added_date=str(datetime.utcnow()))
    db.session.execute(insert_statement)
    db.session.commit()

    flash(f"Song added to playlist '{playlist_name}'!", "success")
    return redirect(url_for('profile'))


@app.route('/admin_error')
def admin_error():
    return render_template('admin_error.html'), 403
