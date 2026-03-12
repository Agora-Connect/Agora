from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User

auth_bp = Blueprint('auth', __name__)

SCSU_DOMAIN = '@stcloudstate.edu'


# ── Landing ───────────────────────────────────────────────────────────────────

@auth_bp.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template('auth/landing.html')


# ── Login ─────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    error = None
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip().lower()
        password   = request.form.get('password', '')
        remember   = bool(request.form.get('remember'))

        # Find user by email or username
        user = (User.query.filter_by(email=identifier).first() or
                User.query.filter_by(username=identifier).first())

        if not user or not user.check_password(password):
            error = 'Invalid email/username or password.'
        else:
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))

    return render_template('auth/login.html', error=error)


# ── Logout ────────────────────────────────────────────────────────────────────

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.landing'))


# ── Signup Step 1: name + email ───────────────────────────────────────────────

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup_step1():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    error = None
    if request.method == 'POST':
        name  = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()

        if not name or not email:
            error = 'Name and email are required.'
        elif not email.endswith(SCSU_DOMAIN):
            error = f'Only {SCSU_DOMAIN} email addresses are allowed.'
        elif User.query.filter_by(email=email).first():
            error = 'An account with this email already exists.'
        else:
            session['signup'] = {'name': name, 'email': email}
            return redirect(url_for('auth.signup_step2'))

    return render_template('auth/signup_step1.html', error=error)


# ── Signup Step 2: major + year ───────────────────────────────────────────────

@auth_bp.route('/signup/step2', methods=['GET', 'POST'])
def signup_step2():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if 'signup' not in session:
        return redirect(url_for('auth.signup_step1'))

    error = None
    if request.method == 'POST':
        major = request.form.get('major', '').strip()
        year  = request.form.get('year', '').strip()
        session['signup']['major'] = major
        session['signup']['year']  = year
        session.modified = True
        return redirect(url_for('auth.signup_step3'))

    return render_template('auth/signup_step2.html', error=error)


# ── Signup Step 3: username + password → create account ──────────────────────

@auth_bp.route('/signup/step3', methods=['GET', 'POST'])
def signup_step3():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if 'signup' not in session:
        return redirect(url_for('auth.signup_step1'))

    error = None
    if request.method == 'POST':
        username         = request.form.get('username', '').strip().lower()
        password         = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not password:
            error = 'Username and password are required.'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif not username.replace('_', '').isalnum():
            error = 'Username can only contain letters, numbers, and underscores.'
        elif User.query.filter_by(username=username).first():
            error = 'This username is already taken.'
        else:
            data = session.pop('signup')
            user = User(
                email      = data['email'],
                username   = username,
                name       = data['name'],
                university = 'Saint Cloud State University',
                major      = data.get('major'),
                year       = data.get('year'),
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('main.home'))

    return render_template('auth/signup_step3.html', error=error)


# ── Remaining auth pages (static renders) ────────────────────────────────────

@auth_bp.route('/signup/verify')
def signup_verify():
    return redirect(url_for('main.home'))


@auth_bp.route('/signup/profile')
@login_required
def signup_profile():
    return render_template('auth/signup_profile.html')


@auth_bp.route('/forgot-password')
def forgot_password():
    return render_template('auth/forgot_password.html')


@auth_bp.route('/forgot-password/sent')
def forgot_password_sent():
    return render_template('auth/forgot_password_sent.html')


@auth_bp.route('/reset-password')
def reset_password():
    return render_template('auth/reset_password.html')
