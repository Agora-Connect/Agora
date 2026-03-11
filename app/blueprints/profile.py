from flask import Blueprint, render_template
from app.mock_data import USERS, POSTS, CURRENT_USER

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/<username>')
def view(username):
    user = next((u for u in USERS if u['username'] == username), None)
    if not user:
        user = CURRENT_USER
    user_posts = [p for p in POSTS if p['author']['username'] == username]
    is_own = (username == CURRENT_USER['username'])
    return render_template('profile/profile.html', user=user, posts=user_posts,
                           is_own=is_own, tab='posts', active_page='profile')


@profile_bp.route('/<username>/edit')
def edit(username):
    return render_template('profile/edit.html', user=CURRENT_USER, active_page='profile')


@profile_bp.route('/<username>/followers')
def followers(username):
    user = next((u for u in USERS if u['username'] == username), CURRENT_USER)
    return render_template('profile/followers.html', user=user, users=USERS, active_page='profile')


@profile_bp.route('/<username>/following')
def following(username):
    user = next((u for u in USERS if u['username'] == username), CURRENT_USER)
    following_users = [u for u in USERS if u.get('is_following')]
    return render_template('profile/following.html', user=user, users=following_users, active_page='profile')
