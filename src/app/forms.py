'''
CS3250 - Software Development Methods and Tools - Fall 2024
Instructor: Thyago Mota
Student(s): Hannah, Amina, Alex, Logan, Patty 
Description: Project 3 - DDR WebSearch


    in progress !!!
'''
from flask_wtf import FlaskForm
from wtforms import *
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
    name = StringField('Name', validators=[DataRequired()])
    about = TextAreaField('About', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

#TODO: test this form
class SearchChartForm(FlaskForm):
    name = StringField("Song name", default=None)
    changingBPM = SelectField("Changing bpm?", choices=["Yes", "No", "Don't care"], default="Don't care")
    artist = StringField("Artist name", default=None)
    # There will likely never be a song added with more than 2000bpm
    # To the best of my knowledge the highest currently in game is Hou with a bpm of 912 
    higherBPM = IntegerField("Highest bpm", default=None, validators=[NumberRange(min=1, max=2000)])
    lowerBPM = IntegerField("Lowest BPM", default=None, validators=[NumberRange(min=1, max=2000)])
    #There is no song currently in the game with a runtime greater than 3 minutes (180 seconds)
    runtime = IntegerField("Song runtime (seconds)", default=None, validators=[NumberRange(min=1, max=180)])
    # There is no song currently with more than 1000 notes, there will never be a song with more than 2000
    licensed = SelectField("Licensed?", choices=["Yes", "No", "Don't care"], default="Don't care")
    # Max difficulty for ddr chart is 19, it is speculated that level 20 charts will be added in the future so we set max to 20
    games = SelectMultipleField("Games", choices=games, default=None)
    highestDifficulty = IntegerField("Highest difficulty rating", default=None, validators=[NumberRange(min=1, max=20)]) 
    lowestDifficulty = IntegerField("Highest difficulty rating", default=None, validators=[NumberRange(min=1, max=20)]) 
    notes = IntegerField("Note count", default=None, validators=[NumberRange(min=1, max=2000)]) 
    difficultyClass = IntegerField("Difficulty class", default=None, 
        choices=["Beginner","Basic", "Difficult", "Expert", "Challenge"])
    excludeDoubles = SelectMultipleField("Exclude doubles?", default="Include doubles charts", 
        choices=["Exclude doubles charts", "Include doubles charts","Include only doubles charts"])
    shockNotes = SelectMultipleField("Exclude songs with shocks?", default="Include shock charts", 
        choices=["Exclude shock charts", "Include shock charts","Include only shock charts"])
    



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
    songName = StringField("Song Name", validators=[DataRequired()])
    artist = StringField("Artist Name", validators=[DataRequired()])
    higherBPM = IntegerField("Highest bpm", validators=[DataRequired()])
    lowerBPM = IntegerField("Lowest bpm", validators=[DataRequired()])
    runtime = IntegerField("Song runtime (seconds)", validators=[DataRequired()])
    licensed = BooleanField("Song is licensed?", default=False)
    #default value for game field is the most recent game, DDR world, as we'll most likely only be adding new charts
    game = SelectField("Game", choices=games, default="DanceDanceRevolution WORLD")
    charts = FieldList(FormField(AddChartForm), min_entries=1)
    submit = SubmitField('Add Song')
    
    @property
    def changingBPM(self):
        # Return True if higherBPM and lowerBPM are different, otherwise False
        if self.higherBPM.data is not None and self.lowerBPM.data is not None:
            return self.higherBPM.data != self.lowerBPM.data
        return False

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