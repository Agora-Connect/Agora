from flask import Blueprint, render_template
from app.mock_data import NOTIFICATIONS

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@notifications_bp.route('/')
def index():
    return render_template('notifications/index.html',
                           notifications=NOTIFICATIONS, active_page='notifications')
