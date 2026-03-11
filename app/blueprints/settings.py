from flask import Blueprint, render_template
from app.mock_data import CURRENT_USER

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('/')
def index():
    return render_template('settings/index.html', active_page='settings')


@settings_bp.route('/account')
def account():
    return render_template('settings/account.html', active_page='settings')


@settings_bp.route('/password')
def password():
    return render_template('settings/password.html', active_page='settings')


@settings_bp.route('/privacy')
def privacy():
    return render_template('settings/privacy.html', active_page='settings')


@settings_bp.route('/notifications')
def notifications():
    return render_template('settings/notifications.html', active_page='settings')


@settings_bp.route('/display')
def display():
    return render_template('settings/display.html', active_page='settings')


@settings_bp.route('/deactivate')
def deactivate():
    return render_template('settings/deactivate.html', active_page='settings')
