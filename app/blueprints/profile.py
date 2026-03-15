import base64
from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user
from app.models import db, User, Post, Follow, UpvoteOnPost, CommentOnPost
from app.utils import enrich_posts

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

MAX_IMAGE_BYTES = 2 * 1024 * 1024  # 2 MB


def _save_image(file_field):
    """Read an uploaded file, validate size/type, return base64 data URL or None."""
    f = request.files.get(file_field)
    if not f or f.filename == '':
        return None
    data = f.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        return None  # silently ignore oversized — UX message handled in template
    mime = f.content_type or 'image/jpeg'
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


@profile_bp.route('/<username>')
@login_required
def view(username):
    user = User.query.filter_by(username=username).first_or_404()
    tab = request.args.get('tab', 'posts')
    is_own = (user.id == current_user.id)
    is_following = (Follow.query.filter_by(follower_id=current_user.id,
                                           followed_id=user.id).first() is not None)

    comments = []
    if tab == 'likes':
        liked_ids = [u.post_id for u in
                     UpvoteOnPost.query.filter_by(user_id=user.id).all()]
        posts = (Post.query.filter(Post.id.in_(liked_ids))
                 .order_by(Post.created_at.desc()).limit(30).all()) if liked_ids else []
    elif tab == 'replies':
        comments = (CommentOnPost.query.filter_by(user_id=user.id)
                    .order_by(CommentOnPost.created_at.desc()).limit(30).all())
        posts = []
    elif tab == 'media':
        posts = (Post.query.filter_by(user_id=user.id)
                 .filter(Post.image_url.isnot(None))
                 .order_by(Post.created_at.desc()).limit(30).all())
    else:
        posts = (Post.query.filter_by(user_id=user.id)
                 .order_by(Post.created_at.desc()).limit(30).all())

    posts = enrich_posts(posts, current_user.id)
    return render_template('profile/profile.html', user=user, posts=posts,
                           comments=comments, is_own=is_own,
                           is_following=is_following, tab=tab,
                           active_page='profile')


@profile_bp.route('/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit(username):
    if username != current_user.username:
        abort(403)

    if request.method == 'POST':
        current_user.name  = request.form.get('name', current_user.name).strip()
        current_user.bio   = request.form.get('bio', '').strip()
        current_user.major = request.form.get('major', '').strip()
        current_user.year  = request.form.get('year', '').strip()

        avatar = _save_image('avatar_file')
        if avatar:
            current_user.avatar_url = avatar

        banner = _save_image('banner_file')
        if banner:
            current_user.banner_url = banner

        db.session.commit()
        return redirect(url_for('profile.view', username=current_user.username))

    return render_template('profile/edit.html', user=current_user, active_page='profile')


@profile_bp.route('/<username>/followers')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    follower_users = [f.follower for f in user.followers.all()]
    return render_template('profile/followers.html', user=user,
                           users=follower_users, active_page='profile')


@profile_bp.route('/<username>/following')
@login_required
def following(username):
    user = User.query.filter_by(username=username).first_or_404()
    following_users = [f.followed for f in user.following.all()]
    return render_template('profile/following.html', user=user,
                           users=following_users, active_page='profile')
