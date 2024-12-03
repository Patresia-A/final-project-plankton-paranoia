'''
CS3250 - Software Development Methods and Tools - Fall 2024
Instructor: Thyago Mota
Student(s): Hannah, Amina, Alex, Logan, Patty 
Description: Project 3 - DDR WebSearch


    in progress !!!
'''
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, PasswordField, TextAreaField, SelectField, IntegerField, SubmitField, BooleanField, FieldList, FormField
from wtforms.validators import DataRequired, EqualTo, NumberRange, Optional, ReadOnly

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
charts = []
class SignUpForm(FlaskForm):
    id = StringField('Id', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    about = TextAreaField('About', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    id = StringField('Id', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

#TODO: test this form
class AddChartForm(FlaskForm):
    difficulty = StringField("Difficulty", validators=[DataRequired()])
    isDoubles = BooleanField("Is Doubles", default=False)
    notes = IntegerField("Notes", validators=[DataRequired()])
    freezeNotes = IntegerField("Freeze Notes", validators=[DataRequired()])
    shockNotes = IntegerField("Shock Notes", default=None)
    difficultyRating = IntegerField("Difficulty Rating", validators=[DataRequired()])
    
#TODO: test this form
class AddSongForm(FlaskForm):
    songName = StringField("Song Name", validators=[DataRequired])
    artist = StringField("Artist Name", validators=[DataRequired])
    higherBPM = IntegerField("Highest bpm", validators=[DataRequired])
    lowerBPM = IntegerField("Lowest bpm", validators=[DataRequired])
    changingBPM = higherBPM.data == lowerBPM.data
    runtime = IntegerField("Song runtime (seconds)", validators=[DataRequired])
    licensed = BooleanField("Song is licensed?", default=False)
    #default value for game field is the most recent game, DDR world, as we'll most likely only be adding new charts
    game = SelectField("Game", choices=games, default="DanceDanceRevolution WORLD")
    charts = FieldList(FormField(AddChartForm), min_entries=1)
    submit = SubmitField('Add Song')

#TODO: test this form
class EditChartForm(FlaskForm):
    difficulty = StringField("Difficulty")
    isDoubles = BooleanField("Is Doubles")
    notes = IntegerField("Notes")
    freezeNotes = IntegerField("Freeze Notes")
    shockNotes = IntegerField("Shock Notes")
    difficultyRating = IntegerField("Difficulty Rating")

    def __init__(self, *args, **kwargs):
        chart = kwargs.pop('chart', None) 
        super().__init__(*args, **kwargs)

        if chart:
            self.difficulty.data = chart.difficulty
            self.isDoubles.data = chart.is_doubles
            self.notes.data = chart.notes
            self.freezeNotes.data = chart.freeze_notes
            self.shockNotes.data = chart.shock_notes if chart.shock_notes is not None else ''
            self.difficultyRating.data = chart.difficulty_rating
            
#TODO: test this form
class EditSongForm(FlaskForm):
    songName = StringField("Song Name")
    artist = StringField("Artist Name")
    higherBPM = IntegerField("Highest BPM")
    lowerBPM = IntegerField("Lowest BPM")
    changingBPM = BooleanField("Changing BPM")
    runtime = IntegerField("Song Runtime (seconds)")
    licensed = BooleanField("Song is licensed?")
    game = SelectField("Game", choices=games)
    
    #each chart is an instance of EditChartForm
    charts = FieldList(FormField(EditChartForm))

    def __init__(self, *args, **kwargs):
        song = kwargs.pop('song', None)
        super().__init__(*args, **kwargs)

        if song:
            self.songName.data = song.song_name
            self.artist.data = song.artist
            self.higherBPM.data = song.higher_bpm
            self.lowerBPM.data = song.lower_bpm
            self.changingBPM.data = song.higher_bpm == song.lower_bpm
            self.runtime.data = song.runtime
            self.licensed.data = song.licensed
            self.game.data = song.game

            for chart in song.charts:
                self.charts.append_entry({
                    'difficulty': chart.difficulty,
                    'isDoubles': chart.is_doubles,
                    'notes': chart.notes,
                    'freezeNotes': chart.freeze_notes,
                    'shockNotes': chart.shock_notes if chart.shock_notes is not None else '',
                    'difficultyRating': chart.difficulty_rating
                })