'''
CS3250 - Software Development Methods and Tools - Fall 2024
Instructor: Thyago Mota
Student(s): Hannah, Amina, Alex, Logan, Patty 
Description: Project 3 - DDR WebSearch

    in progress !!!
'''

from flask_sqlalchemy import SQLAlchemy
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='regular', nullable=False)
    playlists = db.relationship('Playlist', back_populates='user', lazy=True)

    # Relationship to FavoritesLists
    favorites_lists = db.relationship('FavoritesList', back_populates='user', lazy='dynamic', cascade="all, delete-orphan") 

class FavoritesList(db.Model):
    __tablename__ = 'favoriteslists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship back to User
    user = db.relationship('User', back_populates='favorites_lists')

    # Relationship to Songs through the many-to-many table
    songs = db.relationship('Song', secondary='favoriteslistsongs', back_populates='favorites_lists', lazy='dynamic')

class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(200), nullable=False)
    game = db.Column(db.String(200), nullable=False)
    higher_bpm = db.Column(db.Integer, nullable=False)
    lower_bpm = db.Column(db.Integer, nullable=False)
    licensed = db.Column(db.Boolean, nullable=False)
    changing_bpm = db.Column(db.Boolean, nullable=False)
    runtime = db.Column(db.Integer, nullable=False)
    artist = db.Column(db.String(200), nullable=False)

    # Relationship to Charts
    charts = db.relationship('Chart', backref='song', lazy=True)

    # Many-to-many relationship with FavoritesList
    favorites_lists = db.relationship('FavoritesList', secondary='favoriteslistsongs', back_populates='songs', lazy='dynamic')

class Chart(db.Model):
    __tablename__ = 'charts'

    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    is_doubles = db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.Integer, nullable=False)
    freeze_notes = db.Column(db.Integer, nullable=False)
    shock_notes = db.Column(db.Integer)
    difficulty = db.Column(db.String(50), nullable=False)
    difficulty_rating = db.Column(db.Integer, nullable=False)

class FavoritesListSong(db.Model):
    __tablename__ = 'favoriteslistsongs'

    favorites_list_id = db.Column(db.Integer, db.ForeignKey('favoriteslists.id'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), primary_key=True)

class Playlist(db.Model):
    __tablename__ = 'playlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='playlists')

    def __repr__(self):
        return f"<Playlist {self.name}>"