from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import db, Course, Enrollment, Post
from app.utils import enrich_posts

classes_bp = Blueprint('classes', __name__, url_prefix='/classes')


@classes_bp.route('/')
@login_required
def index():
    all_courses = Course.query.order_by(Course.code).all()
    enrolled_ids = {e.course_id for e in
                    Enrollment.query.filter_by(user_id=current_user.id).all()}
    for c in all_courses:
        c.enrolled = c.id in enrolled_ids
    enrolled = [c for c in all_courses if c.enrolled]
    return render_template('classes/index.html', courses=all_courses,
                           enrolled=enrolled, active_page=None)


@classes_bp.route('/<int:course_id>')
@login_required
def detail(course_id):
    course = Course.query.get_or_404(course_id)
    posts = (Post.query.filter_by(course_id=course_id)
             .order_by(Post.created_at.desc()).limit(30).all())
    posts = enrich_posts(posts, current_user.id)
    is_enrolled = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id).first() is not None
    return render_template('classes/detail.html', course=course, posts=posts,
                           is_enrolled=is_enrolled, active_page=None)


@classes_bp.route('/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll(course_id):
    Course.query.get_or_404(course_id)
    existing = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id).first()
    if not existing:
        db.session.add(Enrollment(user_id=current_user.id, course_id=course_id))
        db.session.commit()
    return redirect(url_for('classes.detail', course_id=course_id))


@classes_bp.route('/<int:course_id>/unenroll', methods=['POST'])
@login_required
def unenroll(course_id):
    existing = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
    return redirect(url_for('classes.detail', course_id=course_id))


@classes_bp.route('/create', methods=['POST'])
@login_required
def create():
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not code or not name:
        return redirect(url_for('classes.index'))

    # If course code already exists, just enroll the user
    existing = Course.query.filter_by(code=code).first()
    if existing:
        if not Enrollment.query.filter_by(user_id=current_user.id,
                                          course_id=existing.id).first():
            db.session.add(Enrollment(user_id=current_user.id,
                                      course_id=existing.id))
            db.session.commit()
        return redirect(url_for('classes.detail', course_id=existing.id))

    course = Course(code=code, name=name, description=description or None)
    db.session.add(course)
    db.session.flush()
    db.session.add(Enrollment(user_id=current_user.id, course_id=course.id))
    db.session.commit()
    return redirect(url_for('classes.detail', course_id=course.id))
