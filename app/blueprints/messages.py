from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import db, Message, User, Notification

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')


@messages_bp.route('/')
@login_required
def inbox():
    sent     = Message.query.filter_by(sender_id=current_user.id).all()
    received = Message.query.filter_by(recipient_id=current_user.id).all()

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

    conversations.sort(
        key=lambda c: c['last_message'].sent_at if c['last_message'] else 0,
        reverse=True)
    return render_template('messages/inbox.html',
                           conversations=conversations, active_page='messages')


@messages_bp.route('/search')
@login_required
def search():
    q = request.args.get('q', '').strip()
    users = []
    if q:
        users = (User.query
                 .filter(User.id != current_user.id)
                 .filter(
                     (User.username.ilike(f'%{q}%')) |
                     (User.name.ilike(f'%{q}%'))
                 )
                 .limit(10).all())
    return render_template('messages/search.html', users=users, q=q, active_page='messages')


@messages_bp.route('/<int:partner_id>', methods=['GET', 'POST'])
@login_required
def conversation(partner_id):
    partner = User.query.get_or_404(partner_id)

    if request.method == 'POST':
        content = request.form.get('message', '').strip()
        if content:
            db.session.add(Message(
                sender_id=current_user.id,
                recipient_id=partner_id,
                content=content,
            ))
            # Notify recipient only if they haven't been notified recently
            recent = Notification.query.filter_by(
                recipient_id=partner_id,
                actor_id=current_user.id,
                type='message',
                is_read=False,
            ).first()
            if not recent:
                db.session.add(Notification(
                    recipient_id=partner_id,
                    actor_id=current_user.id,
                    type='message',
                ))
            db.session.commit()
        return redirect(url_for('messages.conversation', partner_id=partner_id))

    messages = (Message.query
                .filter(
                    ((Message.sender_id == current_user.id) & (Message.recipient_id == partner_id)) |
                    ((Message.sender_id == partner_id) & (Message.recipient_id == current_user.id))
                )
                .order_by(Message.sent_at.asc()).all())

    for m in messages:
        if m.recipient_id == current_user.id and not m.is_read:
            m.is_read = True
    db.session.commit()

    return render_template('messages/conversation.html',
                           partner=partner, messages=messages, active_page='messages')
