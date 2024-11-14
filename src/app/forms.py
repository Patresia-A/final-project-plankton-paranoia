'''
CS3250 - Software Development Methods and Tools - Fall 2024
Instructor: Thyago Mota
Student(s): Hannah, Amina, Alex, Logan, Patty 
Description: Project 3 - DDR WebSearch
'''


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

Class SongForm(FlaskForm):

Class GameForm(FlaskForm):

Class ChartForm(FlaskForm):

Class DoublesChartForm(FlaskForm):

Class DifficultyClassificationForm(FlaskForm):

Class FavoriteForm(FlaskForm):
