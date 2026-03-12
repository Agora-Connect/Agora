from flask import Blueprint, render_template
from flask_login import login_required

events_bp = Blueprint('events', __name__, url_prefix='/events')

EVENTS = [
    {'id': 1, 'title': 'Atwood After Dark',   'type': 'Campus Event',
     'description': 'Annual campus night event at Atwood Hall.',
     'date': 'Mar 15, 2026', 'time': '8:00 PM', 'location': 'Atwood Hall',
     'post_count': '2.3K', 'rsvp_count': 340},
    {'id': 2, 'title': 'Huskies First Four',  'type': 'Sports Event',
     'description': 'SCSU basketball tournament game.',
     'date': 'Mar 18, 2026', 'time': '6:00 PM', 'location': 'Halenbeck Hall',
     'post_count': '5.1K', 'rsvp_count': 1200},
    {'id': 3, 'title': 'Hackathon 2026',       'type': 'Tech Event',
     'description': '24-hour hackathon hosted by SCSU CS department. Prizes up to $5000.',
     'date': 'Mar 22, 2026', 'time': '9:00 AM', 'location': 'Engineering Building',
     'post_count': '8.7K', 'rsvp_count': 520},
]


@events_bp.route('/<int:event_id>')
@login_required
def detail(event_id):
    event = next((e for e in EVENTS if e['id'] == event_id), EVENTS[0])
    return render_template('events/detail.html', event=event, active_page=None)
