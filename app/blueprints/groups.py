from flask import Blueprint, render_template, redirect, url_for, request, abort, flash
from flask_login import login_required, current_user
from app.models import db, Group, GroupMembership, GroupPost, Course, Enrollment

groups_bp = Blueprint('groups', __name__, url_prefix='/groups')


@groups_bp.route('/')
@login_required
def index():
    all_groups = (Group.query
                  .filter_by(is_private=False)
                  .order_by(Group.created_at.desc()).all())

    joined_ids = {m.group_id for m in
                  GroupMembership.query.filter_by(user_id=current_user.id).all()}
    for g in all_groups:
        g.is_member = g.id in joined_ids

    my_groups    = [g for g in all_groups if g.is_member]
    other_groups = [g for g in all_groups if not g.is_member]

    return render_template('groups/index.html', my_groups=my_groups,
                           other_groups=other_groups, active_page=None)


@groups_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    enrolled = (Enrollment.query.filter_by(user_id=current_user.id)
                .join(Course).all())
    courses = [e.course for e in enrolled]

    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        course_id   = request.form.get('course_id', type=int)
        is_private  = request.form.get('is_private') == 'on'

        if not name:
            return render_template('groups/create.html',
                                   error='Group name is required.',
                                   courses=courses, active_page=None)

        group = Group(
            name=name,
            description=description or None,
            course_id=course_id or None,
            creator_id=current_user.id,
            is_private=is_private,
        )
        db.session.add(group)
        db.session.flush()

        db.session.add(GroupMembership(
            group_id=group.id,
            user_id=current_user.id,
            role='admin',
        ))
        db.session.commit()
        return redirect(url_for('groups.detail', group_id=group.id))

    return render_template('groups/create.html', courses=courses, active_page=None)


@groups_bp.route('/<int:group_id>')
@login_required
def detail(group_id):
    group = Group.query.get_or_404(group_id)

    membership = GroupMembership.query.filter_by(
        group_id=group_id, user_id=current_user.id).first()
    is_member = membership is not None
    is_admin  = membership and membership.role == 'admin'

    if group.is_private and not is_member:
        abort(403)

    posts   = (GroupPost.query.filter_by(group_id=group_id)
               .order_by(GroupPost.created_at.desc()).limit(50).all())
    members = GroupMembership.query.filter_by(group_id=group_id).all()

    return render_template('groups/detail.html', group=group, posts=posts,
                           members=members, is_member=is_member,
                           is_admin=is_admin, active_page=None)


@groups_bp.route('/<int:group_id>/join', methods=['POST'])
@login_required
def join(group_id):
    Group.query.get_or_404(group_id)
    existing = GroupMembership.query.filter_by(
        group_id=group_id, user_id=current_user.id).first()
    if not existing:
        db.session.add(GroupMembership(
            group_id=group_id,
            user_id=current_user.id,
            role='member',
        ))
        db.session.commit()
    return redirect(url_for('groups.detail', group_id=group_id))


@groups_bp.route('/<int:group_id>/leave', methods=['POST'])
@login_required
def leave(group_id):
    membership = GroupMembership.query.filter_by(
        group_id=group_id, user_id=current_user.id).first()
    if membership:
        if membership.role == 'admin':
            other = GroupMembership.query.filter(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id != current_user.id).first()
            if other:
                other.role = 'admin'
                db.session.delete(membership)
            else:
                db.session.delete(Group.query.get(group_id))
        else:
            db.session.delete(membership)
        db.session.commit()
    return redirect(url_for('groups.index'))


@groups_bp.route('/<int:group_id>/post', methods=['POST'])
@login_required
def post(group_id):
    Group.query.get_or_404(group_id)
    is_member = GroupMembership.query.filter_by(
        group_id=group_id, user_id=current_user.id).first() is not None
    if not is_member:
        abort(403)
    content = request.form.get('content', '').strip()
    if content:
        db.session.add(GroupPost(
            group_id=group_id,
            user_id=current_user.id,
            content=content,
        ))
        db.session.commit()
    return redirect(url_for('groups.detail', group_id=group_id))
