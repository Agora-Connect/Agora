from flask import Blueprint, render_template, redirect, url_for, request
from app.mock_data import FOLLOW_SUGGESTIONS

follow_bp = Blueprint('follow', __name__, url_prefix='/follow')


@follow_bp.route('/')
def suggestions():
    return render_template('follow/suggestions.html',
                           suggestions=FOLLOW_SUGGESTIONS, active_page='follow')


@follow_bp.route('/user/<int:user_id>', methods=['POST'])
def follow_user(user_id):
    return redirect(request.referrer or url_for('follow.suggestions'))
