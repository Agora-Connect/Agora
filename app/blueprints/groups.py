from flask import Blueprint, render_template, redirect, url_for, request, abort, flash
from flask_login import login_required, current_user
from app.models import (db, Group, GroupMembership, GroupPost,
                        GroupInvitation, GroupJoinRequest,
                        Course, Enrollment, Notification, User)

groups_bp = Blueprint('groups', __name__, url_prefix='/groups')


# ── helpers ────────────────────────────────────────────────────────────────────

def _get_membership(group_id, user_id=None):
    uid = user_id or current_user.id
    return GroupMembership.query.filter_by(
        group_id=group_id, user_id=uid).first()


# ── index ──────────────────────────────────────────────────────────────────────

@groups_bp.route('/')
@login_required
def index():
    # Groups the current user belongs to (includes private ones)
    my_memberships = GroupMembership.query.filter_by(user_id=current_user.id).all()
    joined_ids = {m.group_id for m in my_memberships}
    my_groups = (Group.query
                 .filter(Group.id.in_(joined_ids))
                 .order_by(Group.created_at.desc()).all())
    for g in my_groups:
        g.is_admin = _get_membership(g.id) and _get_membership(g.id).role == 'admin'

    # Public groups the user hasn't joined
    other_groups = (Group.query
                    .filter_by(is_private=False)
                    .filter(~Group.id.in_(joined_ids))
                    .order_by(Group.created_at.desc()).all())

    # Pending invitations for current user
    invitations = (GroupInvitation.query
                   .filter_by(invitee_id=current_user.id, status='pending').all())

    return render_template('groups/index.html',
                           my_groups=my_groups,
                           other_groups=other_groups,
                           invitations=invitations,
                           active_page=None)


# ── create ─────────────────────────────────────────────────────────────────────

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

        # Creator is the single admin
        db.session.add(GroupMembership(
            group_id=group.id,
            user_id=current_user.id,
            role='admin',
        ))
        db.session.commit()
        flash(f'"{name}" group created!', 'success')
        return redirect(url_for('groups.detail', group_id=group.id))

    return render_template('groups/create.html', courses=courses, active_page=None)


# ── detail ─────────────────────────────────────────────────────────────────────

@groups_bp.route('/<int:group_id>')
@login_required
def detail(group_id):
    group = Group.query.get_or_404(group_id)
    tab   = request.args.get('tab', 'posts')

    membership = _get_membership(group_id)
    is_member  = membership is not None
    is_admin   = membership and membership.role == 'admin'

    # Private group — must be a member to view
    if group.is_private and not is_member:
        # Check if user has a pending join request
        my_request = GroupJoinRequest.query.filter_by(
            group_id=group_id,
            requester_id=current_user.id).first()
        return render_template('groups/private.html',
                               group=group, my_request=my_request,
                               active_page=None)

    posts   = (GroupPost.query.filter_by(group_id=group_id)
               .order_by(GroupPost.created_at.desc()).limit(50).all())
    members = GroupMembership.query.filter_by(group_id=group_id).all()

    # Admin-only data
    join_requests = []
    if is_admin:
        join_requests = GroupJoinRequest.query.filter_by(
            group_id=group_id, status='pending').all()

    # Check if current user has pending join request
    my_request = None
    if not is_member:
        my_request = GroupJoinRequest.query.filter_by(
            group_id=group_id,
            requester_id=current_user.id).first()

    return render_template('groups/detail.html',
                           group=group, posts=posts,
                           members=members, is_member=is_member,
                           is_admin=is_admin, tab=tab,
                           join_requests=join_requests,
                           my_request=my_request,
                           active_page=None)


# ── join (public groups only) ──────────────────────────────────────────────────

@groups_bp.route('/<int:group_id>/join', methods=['POST'])
@login_required
def join(group_id):
    group = Group.query.get_or_404(group_id)
    if group.is_private:
        abort(403)
    if not _get_membership(group_id):
        db.session.add(GroupMembership(
            group_id=group_id, user_id=current_user.id, role='member'))
        db.session.commit()
    return redirect(url_for('groups.detail', group_id=group_id))


# ── request to join (private groups) ──────────────────────────────────────────

@groups_bp.route('/<int:group_id>/request-join', methods=['POST'])
@login_required
def request_join(group_id):
    group = Group.query.get_or_404(group_id)
    if not group.is_private:
        return redirect(url_for('groups.join', group_id=group_id))
    if _get_membership(group_id):
        return redirect(url_for('groups.detail', group_id=group_id))
    existing = GroupJoinRequest.query.filter_by(
        group_id=group_id, requester_id=current_user.id).first()
    if not existing:
        db.session.add(GroupJoinRequest(
            group_id=group_id, requester_id=current_user.id))
        # Notify admin
        admin_m = GroupMembership.query.filter_by(
            group_id=group_id, role='admin').first()
        if admin_m:
            db.session.add(Notification(
                recipient_id=admin_m.user_id,
                actor_id=current_user.id,
                type='group_join_request',
            ))
        db.session.commit()
        flash('Join request sent! The group admin will review it.', 'success')
    else:
        flash('You already have a pending request for this group.', 'info')
    return redirect(url_for('groups.index'))


# ── leave ──────────────────────────────────────────────────────────────────────

@groups_bp.route('/<int:group_id>/leave', methods=['POST'])
@login_required
def leave(group_id):
    membership = _get_membership(group_id)
    if not membership:
        return redirect(url_for('groups.index'))

    if membership.role == 'admin':
        # Promote the next oldest member to admin before leaving
        next_m = (GroupMembership.query
                  .filter(GroupMembership.group_id == group_id,
                          GroupMembership.user_id != current_user.id)
                  .order_by(GroupMembership.joined_at.asc()).first())
        if next_m:
            next_m.role = 'admin'
            db.session.delete(membership)
        else:
            # Last person — delete the group entirely
            db.session.delete(Group.query.get(group_id))
    else:
        db.session.delete(membership)

    db.session.commit()
    flash('You left the group.', 'info')
    return redirect(url_for('groups.index'))


# ── post in group ──────────────────────────────────────────────────────────────

@groups_bp.route('/<int:group_id>/post', methods=['POST'])
@login_required
def post(group_id):
    Group.query.get_or_404(group_id)
    if not _get_membership(group_id):
        abort(403)
    content = request.form.get('content', '').strip()
    if content:
        db.session.add(GroupPost(
            group_id=group_id, user_id=current_user.id, content=content))
        db.session.commit()
    return redirect(url_for('groups.detail', group_id=group_id))


# ── invite member ──────────────────────────────────────────────────────────────

@groups_bp.route('/<int:group_id>/invite', methods=['POST'])
@login_required
def invite(group_id):
    group = Group.query.get_or_404(group_id)
    m = _get_membership(group_id)
    if not m or m.role != 'admin':
        abort(403)

    username = request.form.get('username', '').strip().lstrip('@')
    invitee  = User.query.filter_by(username=username).first()

    if not invitee:
        flash(f'No user found with username @{username}.', 'error')
        return redirect(url_for('groups.detail', group_id=group_id, tab='manage'))
    if invitee.id == current_user.id:
        flash("You're already in this group.", 'error')
        return redirect(url_for('groups.detail', group_id=group_id, tab='manage'))
    if _get_membership(group_id, invitee.id):
        flash(f'@{username} is already a member.', 'error')
        return redirect(url_for('groups.detail', group_id=group_id, tab='manage'))

    already = GroupInvitation.query.filter_by(
        group_id=group_id, invitee_id=invitee.id, status='pending').first()
    if already:
        flash(f'@{username} already has a pending invitation.', 'info')
        return redirect(url_for('groups.detail', group_id=group_id, tab='manage'))

    db.session.add(GroupInvitation(
        group_id=group_id,
        inviter_id=current_user.id,
        invitee_id=invitee.id,
    ))
    db.session.add(Notification(
        recipient_id=invitee.id,
        actor_id=current_user.id,
        type='group_invite',
    ))
    db.session.commit()
    flash(f'Invitation sent to @{username}!', 'success')
    return redirect(url_for('groups.detail', group_id=group_id, tab='manage'))


# ── respond to invitation ──────────────────────────────────────────────────────

@groups_bp.route('/invitations/<int:inv_id>/accept', methods=['POST'])
@login_required
def accept_invite(inv_id):
    inv = GroupInvitation.query.get_or_404(inv_id)
    if inv.invitee_id != current_user.id:
        abort(403)
    if inv.status == 'pending':
        inv.status = 'accepted'
        if not _get_membership(inv.group_id):
            db.session.add(GroupMembership(
                group_id=inv.group_id,
                user_id=current_user.id,
                role='member',
            ))
        db.session.commit()
        flash(f'You joined "{inv.group.name}"!', 'success')
    return redirect(url_for('groups.detail', group_id=inv.group_id))


@groups_bp.route('/invitations/<int:inv_id>/decline', methods=['POST'])
@login_required
def decline_invite(inv_id):
    inv = GroupInvitation.query.get_or_404(inv_id)
    if inv.invitee_id != current_user.id:
        abort(403)
    inv.status = 'declined'
    db.session.commit()
    flash('Invitation declined.', 'info')
    return redirect(url_for('groups.index'))


# ── approve / decline join requests (admin) ────────────────────────────────────

@groups_bp.route('/<int:group_id>/requests/<int:req_id>/approve', methods=['POST'])
@login_required
def approve_request(group_id, req_id):
    m = _get_membership(group_id)
    if not m or m.role != 'admin':
        abort(403)
    req = GroupJoinRequest.query.get_or_404(req_id)
    if req.group_id != group_id:
        abort(404)
    req.status = 'approved'
    if not _get_membership(group_id, req.requester_id):
        db.session.add(GroupMembership(
            group_id=group_id,
            user_id=req.requester_id,
            role='member',
        ))
    db.session.commit()
    flash(f'{req.requester.display_name} approved!', 'success')
    return redirect(url_for('groups.detail', group_id=group_id, tab='manage'))


@groups_bp.route('/<int:group_id>/requests/<int:req_id>/decline', methods=['POST'])
@login_required
def decline_request(group_id, req_id):
    m = _get_membership(group_id)
    if not m or m.role != 'admin':
        abort(403)
    req = GroupJoinRequest.query.get_or_404(req_id)
    if req.group_id != group_id:
        abort(404)
    req.status = 'declined'
    db.session.commit()
    flash('Request declined.', 'info')
    return redirect(url_for('groups.detail', group_id=group_id, tab='manage'))


# ── transfer admin ─────────────────────────────────────────────────────────────

@groups_bp.route('/<int:group_id>/transfer/<int:user_id>', methods=['POST'])
@login_required
def transfer_admin(group_id, user_id):
    m = _get_membership(group_id)
    if not m or m.role != 'admin':
        abort(403)
    target = _get_membership(group_id, user_id)
    if not target:
        abort(404)
    m.role = 'member'
    target.role = 'admin'
    db.session.commit()
    flash(f'Admin role transferred to {target.user.display_name}.', 'success')
    return redirect(url_for('groups.detail', group_id=group_id, tab='manage'))
