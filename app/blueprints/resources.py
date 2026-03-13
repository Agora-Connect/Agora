from flask import Blueprint, render_template, redirect, url_for, request, abort, flash
from flask_login import login_required, current_user
from app.models import db, Resource, Course, BorrowRequest, Enrollment, Notification

resources_bp = Blueprint('resources', __name__, url_prefix='/resources')


@resources_bp.route('/')
@login_required
def index():
    rtype     = request.args.get('type', '').strip().lower()
    course_id = request.args.get('course_id', type=int)

    q = Resource.query
    if course_id:
        q = q.filter_by(course_id=course_id)
    if rtype and rtype != 'all':
        q = q.filter_by(type=rtype)
    resources = q.order_by(Resource.created_at.desc()).limit(50).all()

    # Attach per-user flags: has pending request?
    pending_ids = {r.resource_id for r in
                   BorrowRequest.query.filter_by(
                       requester_id=current_user.id, status='pending').all()}
    for r in resources:
        r.has_pending_request = r.id in pending_ids

    enrolled = (Enrollment.query.filter_by(user_id=current_user.id)
                .join(Course).all())
    courses = [e.course for e in enrolled]

    incoming_count = BorrowRequest.query.filter_by(
        owner_id=current_user.id, status='pending').count()

    return render_template('resources/index.html', resources=resources,
                           courses=courses, incoming_count=incoming_count,
                           active_type=rtype or 'all', active_page=None)


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
        flash('Resource shared successfully!', 'success')
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
        flash("You can't request your own resource.", 'error')
        return redirect(url_for('resources.index'))
    if not resource.available:
        flash("This resource is currently unavailable.", 'error')
        return redirect(url_for('resources.index'))

    existing = BorrowRequest.query.filter_by(
        resource_id=resource_id, requester_id=current_user.id,
        status='pending').first()
    if existing:
        flash('You already have a pending request for this resource.', 'info')
    else:
        db.session.add(BorrowRequest(
            resource_id=resource_id,
            requester_id=current_user.id,
            owner_id=resource.user_id,
        ))
        # Notify owner
        db.session.add(Notification(
            recipient_id=resource.user_id,
            actor_id=current_user.id,
            type='borrow_request',
        ))
        db.session.commit()
        flash('Request sent! The owner will get back to you.', 'success')
    return redirect(url_for('resources.index'))


@resources_bp.route('/requests')
@login_required
def manage_requests():
    incoming = (BorrowRequest.query
                .filter_by(owner_id=current_user.id)
                .order_by(BorrowRequest.requested_at.desc()).all())
    my_requests = (BorrowRequest.query
                   .filter_by(requester_id=current_user.id)
                   .order_by(BorrowRequest.requested_at.desc()).all())
    return render_template('resources/requests.html',
                           incoming=incoming, my_requests=my_requests,
                           active_page=None)


@resources_bp.route('/requests/<int:request_id>/approve', methods=['POST'])
@login_required
def approve_request(request_id):
    req = BorrowRequest.query.get_or_404(request_id)
    if req.owner_id != current_user.id:
        abort(403)
    req.status = 'approved'
    db.session.commit()
    flash('Request approved!', 'success')
    return redirect(url_for('resources.manage_requests'))


@resources_bp.route('/requests/<int:request_id>/decline', methods=['POST'])
@login_required
def decline_request(request_id):
    req = BorrowRequest.query.get_or_404(request_id)
    if req.owner_id != current_user.id:
        abort(403)
    req.status = 'declined'
    db.session.commit()
    flash('Request declined.', 'info')
    return redirect(url_for('resources.manage_requests'))
