from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, Notification

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@notifications_bp.route('/')
@login_required
def index():
    notifications = (Notification.query
                     .filter_by(recipient_id=current_user.id)
                     .order_by(Notification.created_at.desc())
                     .limit(50).all())
    # Mark all as read
    Notification.query.filter_by(
        recipient_id=current_user.id, is_read=False
    ).update({'is_read': True})
    db.session.commit()
    return render_template('notifications/index.html',
                           notifications=notifications, active_page='notifications')
