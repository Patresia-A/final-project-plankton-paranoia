'''
CS3250 - Software Development Methods and Tools - Fall 2024
Instructor: Thyago Mota
Student(s): Hannah, Amina, Alex, Logan, Patty 
Description: Project 3 - DDR WebSearch


    in progress !!!
'''
from app import app, db
from app.forms import *
from flask import render_template, redirect, url_for
from flask_login import login_required, login_user, logout_user
import bcrypt

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/users/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        if form.password.data == form.confirm_password.data:
            user_id = form.id.data.strip()
            existing_user = User.query.filter_by(id=user_id).first()
            if existing_user is None:
                hashed_passwd = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
                new_user = User(id=user_id, name=form.name.data, about=form.about.data, admin=False, passwd=hashed_passwd)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('search_list_incidents')) 
            else:
                flash("user ID already taken! please choose a different one.")
        else:
            flash("passwords do not match! please try again.")
    return render_template('signup.html', form=form)

@app.route('/users/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.id.data).first()
        if user and bcrypt.checkpw(form.password.data.encode("utf-8"), user.passwd):
            login_user(user)
            flash('login successful!')
            return redirect(url_for('search_list_incidents')) 
        else:
            flash('incorrect username or password. please try again.')
    return render_template('login.html', form=form)

@login_required
@app.route('/users/signout', methods=['GET', 'POST'])
def signout():
    logout_user()
    flash('you have been logged out.')
    return redirect(url_for('login'))

@app.route('/users/profile')
def profile():
    return 'Work in progress...'

@app.route('/songs') # + song code
def songs():
    return 'Work in progress...'

@app.route('/games') # + game code 
def games():
    return 'Work in progress...'

@app.route('/charts')
def charts():
    return 'Work in progress...'

@app.route ('double_charts')
def double_charts():
    return 'Work in progress...'

@app.route('/difficulty_classifications') # + classification code
def difficulty_classifications():
    return 'Work in progress...'

@app.route('/delete_favorite') # + favorite id
def delete_favorite():
    return 'Work in progress...'

@app.route('/add_favorite') # + song code
def add_favorite():
    return 'Work in progress...'

@app.route('favorites') 
def favorites():
    return 'Work in progress...'

@app.route('/search')
def search():
    return 'Work in progress...'
