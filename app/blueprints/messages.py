from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Message, User

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')


@messages_bp.route('/')
@login_required
def inbox():
    # Get distinct conversations for current user
    sent     = Message.query.filter_by(sender_id=current_user.id).all()
    received = Message.query.filter_by(recipient_id=current_user.id).all()

    # Build conversation partners
    partner_ids = set()
    for m in sent:
        partner_ids.add(m.recipient_id)
    for m in received:
        partner_ids.add(m.sender_id)
    partner_ids.discard(current_user.id)

    conversations = []
    for pid in partner_ids:
        partner = User.query.get(pid)
        if not partner:
            continue
        last_msg = (Message.query
                    .filter(
                        ((Message.sender_id == current_user.id) & (Message.recipient_id == pid)) |
                        ((Message.sender_id == pid) & (Message.recipient_id == current_user.id))
                    )
                    .order_by(Message.sent_at.desc()).first())
        unread = Message.query.filter_by(
            sender_id=pid, recipient_id=current_user.id, is_read=False).count()
        conversations.append({
            'partner': partner,
            'last_message': last_msg,
            'unread': unread,
        })

    conversations.sort(key=lambda c: c['last_message'].sent_at if c['last_message'] else 0,
                       reverse=True)
    return render_template('messages/inbox.html',
                           conversations=conversations, active_page='messages')


@messages_bp.route('/<int:partner_id>')
@login_required
def conversation(partner_id):
    partner = User.query.get_or_404(partner_id)
    messages = (Message.query
                .filter(
                    ((Message.sender_id == current_user.id) & (Message.recipient_id == partner_id)) |
                    ((Message.sender_id == partner_id) & (Message.recipient_id == current_user.id))
                )
                .order_by(Message.sent_at.asc()).all())
    # Mark received messages as read
    for m in messages:
        if m.recipient_id == current_user.id and not m.is_read:
            m.is_read = True
    from app.models import db
    db.session.commit()

    # Build conversations list for sidebar
    return render_template('messages/conversation.html',
                           partner=partner, messages=messages,
                           conversations=[], active_page='messages')


@messages_bp.route('/new')
@login_required
def new():
    return redirect(url_for('messages.inbox'))
