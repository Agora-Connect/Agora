import time
import re
import requests as http
from datetime import datetime, timezone
from flask import Blueprint, render_template, request
from flask_login import login_required

events_bp = Blueprint('events', __name__, url_prefix='/events')

HC_BASE     = 'https://huskiesconnect.stcloudstate.edu'
HC_API      = f'{HC_BASE}/api/discovery/event/search'
IMG_BASE    = 'https://se-images.campuslabs.com/clink/images'
CACHE_TTL   = 900  # 15 min

_cache = {'data': None, 'ts': 0}


def _strip_html(html):
    """Remove HTML tags for plain-text preview."""
    if not html:
        return ''
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&[a-z]+;', '', text)
    return ' '.join(text.split())


def _fetch_events(limit=20):
    now = time.time()
    if _cache['data'] and (now - _cache['ts']) < CACHE_TTL:
        return _cache['data']

    try:
        resp = http.get(HC_API, params={
            'endsAfter': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
            'orderByField': 'startsOn',
            'orderByDirection': 'ascending',
            'status': 'Approved',
            'limit': limit,
            'skip': 0,
        }, timeout=6)
        resp.raise_for_status()
        raw = resp.json().get('value', [])

        events = []
        for e in raw:
            img = None
            if e.get('imagePath'):
                img = f"{IMG_BASE}/{e['imagePath']}?preset=medium-sq"
            starts = e.get('startsOn', '')
            try:
                dt = datetime.fromisoformat(starts)
                date_str = dt.strftime('%b %-d')
                time_str = dt.strftime('%-I:%M %p')
            except Exception:
                date_str = starts[:10]
                time_str = ''
            events.append({
                'id':    e.get('id'),
                'name':  e.get('name', 'Untitled'),
                'org':   e.get('organizationName', ''),
                'location': e.get('location') or 'SCSU Campus',
                'date':  date_str,
                'time':  time_str,
                'theme': e.get('theme', ''),
                'categories': e.get('categoryNames', []),
                'benefits':   e.get('benefitNames', []),
                'rsvp':  e.get('rsvpTotal', 0),
                'img':   img,
                'blurb': _strip_html(e.get('description', ''))[:160],
                'url':   f"{HC_BASE}/event/{e.get('id')}",
            })

        _cache['data'] = events
        _cache['ts']   = now
        return events

    except Exception:
        return None


@events_bp.route('/')
@login_required
def index():
    theme = request.args.get('theme', '')
    events = _fetch_events(limit=30)
    if events and theme:
        events = [e for e in events if e['theme'].lower() == theme.lower()]
    error = events is None
    themes = ['Social', 'ThoughtfulLearning', 'Arts', 'Spirituality',
              'CommunityService', 'Fundraising', 'Cultural']
    return render_template('events/index.html', events=events or [],
                           error=error, theme=theme, themes=themes,
                           active_page=None)


@events_bp.route('/<int:event_id>')
@login_required
def detail(event_id):
    # Legacy stub — redirect-capable
    return render_template('events/detail.html',
                           event={'id': event_id, 'title': '', 'type': '',
                                  'description': '', 'date': '', 'time': '',
                                  'location': '', 'post_count': 0, 'rsvp_count': 0},
                           active_page=None)
