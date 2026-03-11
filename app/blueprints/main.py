from flask import Blueprint, render_template, request
from app.mock_data import POSTS, USERS, COURSES

main_bp = Blueprint('main', __name__)


@main_bp.route('/home')
def home():
    tab = request.args.get('tab', 'following')
    return render_template('main/home.html', posts=POSTS, tab=tab, active_page='home')


@main_bp.route('/explore')
def explore():
    return render_template('main/explore.html', active_page='explore')


@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    tab = request.args.get('tab', 'top')
    results = [p for p in POSTS if query.lower() in p['content'].lower()] if query else []
    return render_template('main/search.html', query=query, results=results, tab=tab, active_page='explore')
