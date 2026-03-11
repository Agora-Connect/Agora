from flask import Blueprint, render_template
from app.mock_data import EVENTS

events_bp = Blueprint('events', __name__, url_prefix='/events')


@events_bp.route('/<int:event_id>')
def detail(event_id):
    event = next((e for e in EVENTS if e['id'] == event_id), EVENTS[0])
    return render_template('events/detail.html', event=event, active_page=None)
