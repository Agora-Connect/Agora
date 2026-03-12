from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Post, Bookmark
from app.utils import enrich_posts

bookmarks_bp = Blueprint('bookmarks', __name__, url_prefix='/bookmarks')


@bookmarks_bp.route('/')
@login_required
def index():
    bookmarked_post_ids = [b.post_id for b in
                           current_user.bookmarks.order_by(Bookmark.created_at.desc()).all()]
    posts = Post.query.filter(Post.id.in_(bookmarked_post_ids)).all()
    # Preserve bookmark order
    post_map = {p.id: p for p in posts}
    ordered  = [post_map[pid] for pid in bookmarked_post_ids if pid in post_map]
    ordered  = enrich_posts(ordered, current_user.id)
    return render_template('bookmarks/index.html', posts=ordered, active_page='bookmarks')
