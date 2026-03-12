from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import db, Post, Course, Enrollment, Follow
from app.utils import enrich_posts

main_bp = Blueprint('main', __name__)


@main_bp.route('/home')
@login_required
def home():
    tab = request.args.get('tab', 'following')

    if tab == 'following':
        followed_ids = [f.followed_id for f in current_user.following.all()]
        followed_ids.append(current_user.id)
        posts = (Post.query
                 .filter(Post.user_id.in_(followed_ids))
                 .order_by(Post.created_at.desc())
                 .limit(50).all())
    else:
        posts = (Post.query
                 .order_by(Post.created_at.desc())
                 .limit(50).all())

    posts = enrich_posts(posts, current_user.id)

    enrolled = (Enrollment.query
                .filter_by(user_id=current_user.id)
                .join(Course).all())
    courses = [e.course for e in enrolled]

    return render_template('main/home.html', posts=posts, tab=tab,
                           courses=courses, active_page='home')


@main_bp.route('/explore')
@login_required
def explore():
    from sqlalchemy import func
    from app.models import Tag, post_tags
    # Top 10 tags by usage
    trending = (db.session.query(Tag.name, func.count(post_tags.c.post_id).label('cnt'))
                .join(post_tags, Tag.id == post_tags.c.tag_id)
                .group_by(Tag.id)
                .order_by(func.count(post_tags.c.post_id).desc())
                .limit(10).all())

    from app.models import Follow, User
    followed_ids = {f.followed_id for f in current_user.following.all()}
    followed_ids.add(current_user.id)
    suggestions = (User.query
                   .filter(~User.id.in_(followed_ids))
                   .order_by(User.reputation_score.desc())
                   .limit(5).all())

    return render_template('main/explore.html', trending_tags=trending,
                           suggestions=suggestions, active_page='explore')


@main_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    tab   = request.args.get('tab', 'top')

    results = []
    if query:
        results = (Post.query
                   .filter(Post.content.ilike(f'%{query}%'))
                   .order_by(Post.created_at.desc())
                   .limit(30).all())
        results = enrich_posts(results, current_user.id)

    return render_template('main/search.html', query=query, results=results,
                           tab=tab, active_page='explore')
