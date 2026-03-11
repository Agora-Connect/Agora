from flask import Blueprint, render_template, redirect, url_for, request
from app.mock_data import POSTS, CURRENT_USER

posts_bp = Blueprint('posts', __name__, url_prefix='/post')


@posts_bp.route('/<int:post_id>')
def detail(post_id):
    post = next((p for p in POSTS if p['id'] == post_id), POSTS[0])
    return render_template('posts/detail.html', post=post, active_page=None)


@posts_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        return redirect(url_for('main.home'))
    return render_template('posts/create.html', active_page=None)


@posts_bp.route('/<int:post_id>/like', methods=['POST'])
def like(post_id):
    return redirect(request.referrer or url_for('main.home'))


@posts_bp.route('/<int:post_id>/repost', methods=['POST'])
def repost(post_id):
    return redirect(request.referrer or url_for('main.home'))


@posts_bp.route('/<int:post_id>/bookmark', methods=['POST'])
def bookmark(post_id):
    return redirect(request.referrer or url_for('main.home'))


@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
def delete(post_id):
    return redirect(url_for('main.home'))
