'''
CS3250 - Software Development Methods and Tools - Fall 2024
Instructor: Thyago Mota
Student(s): Hannah, Amina, Alex, Logan, Patty
Description: Project 3 - DDR WebSearch


    in progress !!!
'''
from flask_wtf import FlaskForm
from wtforms import (
    StringField, EmailField, PasswordField, SubmitField, SelectField,
    SelectMultipleField, IntegerField, BooleanField, FieldList, FormField
)
from wtforms.validators import (
    DataRequired, EqualTo, NumberRange, Email, Optional
)

games = [
    "DanceDanceRevolution",
    "DanceDanceRevolution Internet Ranking Version",
    "DanceDanceRevolution 2ndMIX",
    "DanceDanceRevolution 2ndMIX / DanceDanceRevolution 2ndMIX LINK VERSION",
    "DanceDanceRevolution 2ndMIX CLUB VERSiON",
    "DanceDanceRevolution 2ndMIX CLUB VERSiON 2",
    "DanceDanceRevolution 3rdMIX",
    "DanceDanceRevolution 3rdMIX PLUS",
    "DanceDanceRevolution 4thMIX",
    "DanceDanceRevolution 4thMIX PLUS",
    "DanceDanceRevolution 5thMIX",
    "DDRMAX -DanceDanceRevolution 6thMIX-",
    "DDRMAX2 -DanceDanceRevolution 7thMIX-",
    "DanceDanceRevolution EXTREME",
    "DanceDanceRevolution SuperNOVA",
    "DanceDanceRevolution SuperNOVA2",
    "DanceDanceRevolution X",
    "DanceDanceRevolution X2",
    "DanceDanceRevolution X3 VS 2ndMIX",
    "DanceDanceRevolution (2013)",
    "DanceDanceRevolution (2014)",
    "DanceDanceRevolution A",
    "DanceDanceRevolution A20",
    "DanceDanceRevolution A20 PLUS",
    "DanceDanceRevolution A3",
    "DanceDanceRevolution WORLD"
]
reversedGames = []
charts = []


class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password')
            ]
        )
    submit = SubmitField('Sign up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# test this form


class SearchChartForm(FlaskForm):
    songName = StringField("Song name", default=None)
    changingBPM = SelectField(
        "Changing bpm?", choices=["Yes", "No", "Don't care"],
        default="Don't care"
    )
    artist = StringField("Artist name", default=None)
    # There will likely never be a song added with more than 2000bpm
    # To the best of my knowledge the highest currently in game is
    # Hou with a bpm of 912
    higherBPM = IntegerField(
        "Highest bpm",
        default=None,
        validators=[
            Optional(),
            NumberRange(min=1, max=2000)
        ]
    )
    lowerBPM = IntegerField(
        "Lowest BPM",
        default=None,
        validators=[
            Optional(),
            NumberRange(min=1, max=2000)
        ]
    )
    # there is no song currently in the game with a runtime greater
    # than 3 minutes (180 seconds)
    maxRuntime = IntegerField(
        "Max song runtime (seconds)",
        default=None,
        validators=[
            Optional(),
            NumberRange(min=1, max=180)
        ]
    )

    licensed = SelectField(
        "Licensed?",
        choices=["Yes", "No", "Don't care"],
        default="Don't care"
    )

    games = SelectMultipleField(
        "Games",
        choices=games,
        default=None
    )

    highestDifficulty = IntegerField(
        "Highest difficulty rating",
        default=None,
        validators=[
            Optional(),
            NumberRange(min=1, max=20)
        ]
    )

    lowestDifficulty = IntegerField(
        "Lowest difficulty rating",
        default=None,
        validators=[
            Optional(),
            NumberRange(min=1, max=20)
        ]
    )
    maxNotes = IntegerField(
        "Max note count",
        default=None,
        validators=[
            Optional(),
            NumberRange(min=1, max=2000)
        ]
    )
    minNotes = IntegerField(
        "Min note count",
        default=None,
        validators=[
            Optional(),
            NumberRange(min=1, max=2000)
        ]
    )

    difficultyClass = SelectMultipleField(
        "Difficulty class",
        default=None,
        choices=[
            "beginner",
            "basic",
            "difficult",
            "expert",
            "challenge"
        ]
    )
    excludeDoubles = SelectField(
        "Exclude doubles?",
        default="Include doubles charts",
        choices=[
            "Exclude doubles charts",
            "Include doubles charts",
            "Include only doubles charts"
        ]
    )
    excludeShocks = SelectField(
        "Exclude shocks?",
        default="Include shock charts",
        choices=[
            "Exclude shock charts",
            "Include shock charts",
            "Include only shock charts"
        ]
    )
    submit = SubmitField('Search Songs')
# test this form


class AddChartForm(FlaskForm):
    difficulty = StringField("Difficulty", validators=[DataRequired()])
    isDoubles = BooleanField("Is Doubles", default=False)
    notes = IntegerField("Notes", validators=[DataRequired()])
    freezeNotes = IntegerField("Freeze Notes", validators=[DataRequired()])
    shockNotes = IntegerField("Shock Notes", default=None)


difficultyRating = IntegerField(
    "Difficulty Rating",
    validators=[DataRequired()]
)
submit = SubmitField('Add chart')

# class DeleteSongForm(FlaskForm):


# test this form
class AddSongForm(FlaskForm):
    songName = StringField("Song Name", validators=[DataRequired()])
    artist = StringField("Artist Name", validators=[DataRequired()])
    higherBPM = IntegerField("Highest bpm", validators=[DataRequired()])
    lowerBPM = IntegerField("Lowest bpm", validators=[DataRequired()])
    runtime = IntegerField(
        "Song runtime (seconds)",
        validators=[DataRequired()]
    )
    licensed = BooleanField(
        "Song is licensed?",
        default=False
    )
    # default value for game field is the most recent game,
    # DDR world, as we'll most likely only be adding new charts
    game = SelectField(
        "Game",
        choices=games,
        default="DanceDanceRevolution WORLD"
    )
    charts = FieldList(FormField(AddChartForm), min_entries=1)
    submit = SubmitField('Add Song')

    @property
    def changingBPM(self):
        # Return True if higherBPM and lowerBPM are different, otherwise False
        if self.higherBPM.data is not None and self.lowerBPM.data is not None:
            return self.higherBPM.data != self.lowerBPM.data
        return False


# test this form
class EditChartForm(FlaskForm):
    difficulty = StringField("Difficulty")
    isDoubles = BooleanField("Is Doubles")
    notes = IntegerField("Notes", validators=[Optional()])
    freezeNotes = IntegerField(
        "Freeze Notes",
        validators=[Optional()],
        default=0
    )
    shockNotes = IntegerField(
        "Shock Notes",
        validators=[Optional()],
        default=0
    )
    difficultyRating = IntegerField(
        "Difficulty Rating",
        validators=[Optional()]
    )

    def __init__(self, *args, **kwargs):
        chart = kwargs.pop('chart', None)
        super().__init__(*args, **kwargs)

        if chart:
            self.difficulty.data = chart.difficulty
            self.isDoubles.data = chart.is_doubles
            self.notes.data = chart.notes
            self.freezeNotes.data = chart.freeze_notes
            self.shockNotes.data = (
                chart.shock_notes if chart.shock_notes is not None else ''
            )
            self.difficultyRating.data = chart.difficulty_rating
    submit = SubmitField('Edit Chart')

# test this form


class EditSongForm(FlaskForm):
    songName = StringField("Song Name")
    artist = StringField("Artist Name")
    higherBPM = IntegerField("Highest BPM")
    lowerBPM = IntegerField("Lowest BPM")
    runtime = IntegerField("Song Runtime (seconds)")
    licensed = BooleanField("Song is licensed?")
    game = SelectField("Game", choices=games)

    # Each chart is an instance of EditChartForm
    charts = FieldList(FormField(EditChartForm))

    @property
    def changingBPM(self):
        # Return True if higherBPM and lowerBPM are different, otherwise False
        if self.higherBPM.data is not None and self.lowerBPM.data is not None:
            return self.higherBPM.data != self.lowerBPM.data
        return False

    def __init__(self, *args, **kwargs):
        song = kwargs.pop('song', None)
        super().__init__(*args, **kwargs)

        if song:
            self.songName.data = song.song_name
            self.artist.data = song.artist
            self.higherBPM.data = song.higher_bpm
            self.lowerBPM.data = song.lower_bpm
            self.runtime.data = song.runtime
            self.licensed.data = song.licensed
            self.game.data = song.game

            # Populate the charts field
            for chart in song.charts:
                self.charts.append_entry({
                    'difficulty': chart.difficulty,
                    'isDoubles': chart.is_doubles,
                    'notes': chart.notes,
                    'freezeNotes': chart.freeze_notes,
                    'shockNotes': (
                        chart.shock_notes
                        if chart.shock_notes is not None
                        else ''
                    ),
                    'difficultyRating': chart.difficulty_rating,
                })


class UpdateNameForm(FlaskForm):
    name = StringField("New Name", validators=[DataRequired()])
    submit_name = SubmitField("Change Name")


class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField(
        'Current Password',
        validators=[DataRequired()]
    )
    new_password = PasswordField(
        'New Password',
        validators=[DataRequired()]
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('new_password')]
    )
    submit_password = SubmitField('Change Password')


class CreatePlaylistForm(FlaskForm):
    name = StringField("Playlist Name", validators=[DataRequired()])
    submit_playlist = SubmitField("Create Playlist")


class UpdateEmailForm(FlaskForm):
    new_email = StringField(
        'New Email',
        validators=[DataRequired(), Email()]
    )
    confirm_email = StringField(
        'Confirm New Email',
        validators=[DataRequired(), EqualTo('new_email')]
    )
    submit_email = SubmitField('Update Email')
