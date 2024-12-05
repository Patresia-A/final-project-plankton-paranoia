'''
CS3250 - Software Development Methods and Tools - Fall 2024
Instructor: Thyago Mota
Student(s): Hannah, Amina, Alex, Logan, Patty 
Description: Project 3 - DDR WebSearch


    in progress !!!
'''

from flask import Flask
import os
import click
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache
from flask_migrate import Migrate

app = Flask('DDR DATABASE', template_folder="app/templates", static_folder="app/static") # feel free to change this! 
app.secret_key = os.environ.get('SECRET_KEY', '  ') # change this to a more secure secret key

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/project3_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # initialize db here
# create database tables if they don't exist
with app.app_context(): 
    db.create_all()

# login manager
login_manager = LoginManager()
login_manager.init_app(app)


cache = Cache()
cache.init_app(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# import models after db initialization
from app.models import User  

# CLI command for creating admin
@click.command('create-admin')
@with_appcontext
@click.option('--username', prompt='Admin username')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--name', prompt='Admin name')
def create_admin_command(username, password, name):
    """Create a new admin user"""
    try:
        if User.query.get(username):  # Check if the username already exists
            click.echo('Error: Username already exists')
            return

        # hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # create admin user
        admin = User(
            id=username,
            name=name,
            about='System Administrator',
            admin=True,
            passwd=hashed_password
        )

        db.session.add(admin)
        db.session.commit()
        click.echo('Admin user created successfully')

    except Exception as e:
        db.session.rollback()
        click.echo(f'Error creating admin user: {str(e)}')

app.cli.add_command(create_admin_command)


@login_manager.user_loader
def load_user(id):
    try: 
        return User.query.get(id)  
    except Exception as e: 
        click.echo(f'Error loading user: {str(e)}')
        return None

from app import routes  
