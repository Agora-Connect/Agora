from flask import Blueprint, render_template, request, redirect, url_for
from app.mock_data import CONVERSATIONS

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')


@messages_bp.route('/')
def inbox():
    return render_template('messages/inbox.html',
                           conversations=CONVERSATIONS, active_page='messages')


@messages_bp.route('/<int:conversation_id>')
def conversation(conversation_id):
    convo = next((c for c in CONVERSATIONS if c['id'] == conversation_id), CONVERSATIONS[0])
    return render_template('messages/conversation.html',
                           conversation=convo, conversations=CONVERSATIONS, active_page='messages')


@messages_bp.route('/new')
def new():
    return redirect(url_for('messages.inbox'))
