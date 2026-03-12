from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user
from app.models import db, Resource, Course, BorrowRequest, Enrollment

resources_bp = Blueprint('resources', __name__, url_prefix='/resources')


@resources_bp.route('/')
@login_required
def index():
    course_id = request.args.get('course_id', type=int)
    q = Resource.query
    if course_id:
        q = q.filter_by(course_id=course_id)
    resources = q.order_by(Resource.created_at.desc()).limit(50).all()

    enrolled = (Enrollment.query.filter_by(user_id=current_user.id)
                .join(Course).all())
    courses = [e.course for e in enrolled]

    return render_template('resources/index.html', resources=resources,
                           courses=courses, active_page=None)


@resources_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        rtype       = request.form.get('type', '').strip()
        description = request.form.get('description', '').strip()
        course_id   = request.form.get('course_id', type=int)

        if not title or not rtype or not course_id:
            enrolled = (Enrollment.query.filter_by(user_id=current_user.id)
                        .join(Course).all())
            courses = [e.course for e in enrolled]
            return render_template('resources/create.html',
                                   error='Title, type, and course are required.',
                                   courses=courses, active_page=None)

        r = Resource(user_id=current_user.id, course_id=course_id,
                     title=title, type=rtype, description=description)
        db.session.add(r)
        db.session.commit()
        return redirect(url_for('resources.index'))

    enrolled = (Enrollment.query.filter_by(user_id=current_user.id)
                .join(Course).all())
    courses = [e.course for e in enrolled]
    return render_template('resources/create.html', courses=courses, active_page=None)


@resources_bp.route('/<int:resource_id>/borrow', methods=['POST'])
@login_required
def borrow(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    if resource.user_id == current_user.id:
        abort(400)
    existing = BorrowRequest.query.filter_by(
        resource_id=resource_id, requester_id=current_user.id,
        status='pending').first()
    if not existing:
        db.session.add(BorrowRequest(
            resource_id=resource_id,
            requester_id=current_user.id,
            owner_id=resource.user_id,
        ))
        db.session.commit()
    return redirect(url_for('resources.index'))
