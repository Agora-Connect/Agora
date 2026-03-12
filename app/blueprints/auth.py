from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User

auth_bp = Blueprint('auth', __name__)

SCSU_DOMAIN = '@stcloudstate.edu'


@auth_bp.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template('auth/landing.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    error = None
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip().lower()
        password   = request.form.get('password', '')

        user = (User.query.filter_by(email=identifier).first() or
                User.query.filter_by(username=identifier).first())

        if not user or not user.check_password(password):
            error = 'Invalid email/username or password.'
        else:
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))

    return render_template('auth/login.html', error=error)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.landing'))


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    error = None
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not username or not password:
            error = 'All fields are required.'
        elif not email.endswith(SCSU_DOMAIN):
            error = f'Only {SCSU_DOMAIN} email addresses are allowed.'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters.'
        elif not username.replace('_', '').isalnum():
            error = 'Username can only contain letters, numbers, and underscores.'
        elif User.query.filter_by(email=email).first():
            error = 'An account with this email already exists.'
        elif User.query.filter_by(username=username).first():
            error = 'This username is already taken.'
        else:
            user = User(
                email      = email,
                username   = username,
                name       = name,
                university = 'Saint Cloud State University',
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('main.home'))

    return render_template('auth/signup.html', error=error)
