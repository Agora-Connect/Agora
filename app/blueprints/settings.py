from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import db

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('/')
@login_required
def index():
    return render_template('settings/index.html', active_page='settings')


@settings_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip().lower()
        bio      = request.form.get('bio', '').strip()
        major    = request.form.get('major', '').strip()
        year     = request.form.get('year', '').strip()

        from app.models import User
        if username and username != current_user.username:
            if User.query.filter_by(username=username).first():
                return render_template('settings/account.html',
                                       error='Username already taken.', active_page='settings')
            current_user.username = username

        if name:
            current_user.name = name
        current_user.bio   = bio
        current_user.major = major
        current_user.year  = year
        db.session.commit()
        return redirect(url_for('settings.account'))

    return render_template('settings/account.html', active_page='settings')


@settings_bp.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    error = None
    success = None
    if request.method == 'POST':
        current_pw  = request.form.get('current_password', '')
        new_pw      = request.form.get('new_password', '')
        confirm_pw  = request.form.get('confirm_password', '')

        if not current_user.check_password(current_pw):
            error = 'Current password is incorrect.'
        elif len(new_pw) < 8:
            error = 'New password must be at least 8 characters.'
        elif new_pw != confirm_pw:
            error = 'Passwords do not match.'
        else:
            current_user.set_password(new_pw)
            db.session.commit()
            success = 'Password updated successfully.'

    return render_template('settings/password.html', error=error,
                           success=success, active_page='settings')


@settings_bp.route('/privacy')
@login_required
def privacy():
    return render_template('settings/privacy.html', active_page='settings')


@settings_bp.route('/notifications')
@login_required
def notifications():
    return render_template('settings/notifications.html', active_page='settings')


@settings_bp.route('/display')
@login_required
def display():
    return render_template('settings/display.html', active_page='settings')


@settings_bp.route('/deactivate')
@login_required
def deactivate():
    return render_template('settings/deactivate.html', active_page='settings')
