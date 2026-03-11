from flask import Blueprint, render_template
from app.mock_data import POSTS

bookmarks_bp = Blueprint('bookmarks', __name__, url_prefix='/bookmarks')


@bookmarks_bp.route('/')
def index():
    bookmarked = [p for p in POSTS if p.get('is_bookmarked_by_me')]
    return render_template('bookmarks/index.html', posts=bookmarked, active_page='bookmarks')
