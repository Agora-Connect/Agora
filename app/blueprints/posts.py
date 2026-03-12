from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user
from app.models import db, Post, Course, Tag, UpvoteOnPost, Repost, Bookmark, \
                       CommentOnPost, Notification, Enrollment
from app.utils import enrich_posts

posts_bp = Blueprint('posts', __name__, url_prefix='/post')


@posts_bp.route('/<int:post_id>')
@login_required
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    enrich_posts([post], current_user.id)
    comments = (CommentOnPost.query
                .filter_by(post_id=post_id)
                .order_by(CommentOnPost.created_at.asc()).all())
    return render_template('posts/detail.html', post=post,
                           comments=comments, active_page=None)


@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        content      = request.form.get('content', '').strip()
        course_id    = request.form.get('course_id', type=int)
        is_anonymous = bool(request.form.get('is_anonymous'))
        tag_str      = request.form.get('tags', '')

        if not content:
            enrolled = (Enrollment.query.filter_by(user_id=current_user.id)
                        .join(Course).all())
            courses = [e.course for e in enrolled]
            return render_template('posts/create.html', error='Post content is required.',
                                   courses=courses, active_page=None)

        post = Post(user_id=current_user.id, course_id=course_id,
                    content=content, is_anonymous=is_anonymous)

        # Handle tags
        for raw in tag_str.split(','):
            name = raw.strip().lower().lstrip('#')
            if name:
                tag = Tag.query.filter_by(name=name).first() or Tag(name=name)
                post._tags.append(tag)

        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.home'))

    enrolled = (Enrollment.query.filter_by(user_id=current_user.id)
                .join(Course).all())
    courses = [e.course for e in enrolled]
    return render_template('posts/create.html', courses=courses, active_page=None)


@posts_bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    existing = UpvoteOnPost.query.filter_by(post_id=post_id,
                                            user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(UpvoteOnPost(post_id=post_id, user_id=current_user.id))
        if post.user_id != current_user.id:
            db.session.add(Notification(
                recipient_id=post.user_id,
                actor_id=current_user.id,
                type='like',
                post_id=post_id,
            ))
    db.session.commit()
    return redirect(request.referrer or url_for('main.home'))


@posts_bp.route('/<int:post_id>/repost', methods=['POST'])
@login_required
def repost(post_id):
    post = Post.query.get_or_404(post_id)
    existing = Repost.query.filter_by(post_id=post_id,
                                      user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(Repost(post_id=post_id, user_id=current_user.id))
        if post.user_id != current_user.id:
            db.session.add(Notification(
                recipient_id=post.user_id,
                actor_id=current_user.id,
                type='repost',
                post_id=post_id,
            ))
    db.session.commit()
    return redirect(request.referrer or url_for('main.home'))


@posts_bp.route('/<int:post_id>/bookmark', methods=['POST'])
@login_required
def bookmark(post_id):
    Post.query.get_or_404(post_id)
    existing = Bookmark.query.filter_by(post_id=post_id,
                                        user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(Bookmark(post_id=post_id, user_id=current_user.id))
    db.session.commit()
    return redirect(request.referrer or url_for('main.home'))


@posts_bp.route('/<int:post_id>/comment', methods=['POST'])
@login_required
def comment(post_id):
    post    = Post.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()
    if content:
        db.session.add(CommentOnPost(post_id=post_id, user_id=current_user.id,
                                     content=content))
        if post.user_id != current_user.id:
            db.session.add(Notification(
                recipient_id=post.user_id,
                actor_id=current_user.id,
                type='reply',
                post_id=post_id,
            ))
        db.session.commit()
    return redirect(url_for('posts.detail', post_id=post_id))


@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('main.home'))
