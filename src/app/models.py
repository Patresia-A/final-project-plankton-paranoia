'''
CS3250 - Software Development Methods and Tools - Fall 2024
Instructor: Thyago Mota
Student(s): Hannah, Amina, Alex, Logan, Patty 
Description: Project 3 - DDR WebSearch
'''

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from wtforms.validators import DataRequired
from app import db

Class User(db.Model, Usermixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    about = db.Column(db.Text)
    admin = db.Column(db.Boolean, default=False)
    passwd = db.Column(db.String(255), nullable=False)

    @property
    def is_active(self):
        return True
    @property
    def is_authenticated(self):
        return True
    @propety
    def is_anonymous(self):
        return False

Class Song(db.Model):
    __tablename__ = 'songs'
    code = db.Column(db.String(10), primary_key=True)
    description = db.Column(db.String, nullable=False)

    def __str__(self):
        return f'{self.code},{self.description}

Class Game(db.Model):
    __tablename__ = 'games'
    code = db.Column(db.String(10), primary_key=True)
    description = db.Column(db.String, nullable=False)

    def __str__(self):
        return f'{self.code},{self.description}

Class Chart(db.Model):
    __tablename__ = 'charts'
    id = db.Column(db.Integer, primary_key=True)

    def __str__(self):
        return f'{self.id}'


Class DoublesChart(db.Model):

Class DifficultyClassification(db.Model):
    __tablename__ = 'difficulty_classifications'
    code = db.Column(db.String(10), primary_key=True)

    def __str__(self):
        return f'{self.code}'

Class FavoritesList(db.Model):
    __tablename__ = 'favorites_lists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_code = db.Column(db.String(10), db.ForeignKey('songs.code'), nullable=False)

    def __str__(self):
        return f'{self.id},{self.user_id},{self.song_code}'

