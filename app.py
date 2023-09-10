from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import bcrypt

# Setting up Flask app to connect with mongodb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost/your_database_name'

mongo = PyMongo(app)

# User class will represent user objects and include methods required for user authentication:


class User(UserMixin):
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


# Create registration and login forms

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Create Registration and Login Routes

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = mongo.db.users.find_one(
            {'username': form.username.data})
        if existing_user is None:
            hashed_password = bcrypt.hashpw(
                form.password.data.encode('utf-8'), bcrypt.gensalt())
            mongo.db.users.insert_one({
                'username': form.username.data,
                'email': form.email.data,
                'password': hashed_password
            })
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Please choose another.', 'danger')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({'username': form.username.data})
        if user and bcrypt.checkpw(form.password.data.encode('utf-8'), user['password']):
            user_obj = User(user['username'], user['email'], user['password'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login credentials. Please try again.', 'danger')
    return render_template('login.html', form=form)
