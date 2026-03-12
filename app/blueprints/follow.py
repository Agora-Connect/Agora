from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import db, User, Follow, Notification

follow_bp = Blueprint('follow', __name__, url_prefix='/follow')


@follow_bp.route('/')
@login_required
def suggestions():
    # Users not followed by current user (excluding self)
    followed_ids = {f.followed_id for f in current_user.following.all()}
    followed_ids.add(current_user.id)
    suggestions = (User.query
                   .filter(~User.id.in_(followed_ids))
                   .order_by(User.reputation_score.desc())
                   .limit(20).all())
    return render_template('follow/suggestions.html',
                           suggestions=suggestions, active_page='follow')


@follow_bp.route('/user/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    if user_id == current_user.id:
        return redirect(request.referrer or url_for('follow.suggestions'))

    existing = Follow.query.filter_by(follower_id=current_user.id,
                                      followed_id=user_id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(Follow(follower_id=current_user.id, followed_id=user_id))
        db.session.add(Notification(
            recipient_id=user_id,
            actor_id=current_user.id,
            type='follow',
        ))
    db.session.commit()
    return redirect(request.referrer or url_for('follow.suggestions'))
