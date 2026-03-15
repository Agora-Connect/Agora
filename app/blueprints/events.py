import time
import re
import requests as http
from datetime import datetime, timezone
from flask import Blueprint, render_template, request
from flask_login import login_required

events_bp = Blueprint('events', __name__, url_prefix='/events')

HC_BASE   = 'https://huskiesconnect.stcloudstate.edu'
HC_API    = f'{HC_BASE}/api/discovery/event/search'
HC_NEWS   = f'{HC_BASE}/api/discovery/newsfeed/search'
HC_ORGS   = f'{HC_BASE}/api/discovery/organization/search'
IMG_BASE  = 'https://se-images.campuslabs.com/clink/images'
CACHE_TTL = 900  # 15 min

_cache      = {'data': None, 'ts': 0}
_news_cache = {'data': None, 'ts': 0}
_orgs_cache = {'data': None, 'ts': 0}


def _strip_html(html):
    if not html:
        return ''
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&[a-z]+;', '', text)
    return ' '.join(text.split())


def _img(path, preset='medium-sq'):
    return f"{IMG_BASE}/{path}?preset={preset}" if path else None


def _fmt_dt(iso):
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime('%b %-d'), dt.strftime('%-I:%M %p')
    except Exception:
        return iso[:10], ''


def _parse_dt(raw):
    """Parse API datetime string to UTC-aware datetime. Returns None on failure."""
    if not raw:
        return None
    try:
        # Handle both 'Z' suffix and offset like '-06:00'
        s = raw.replace('Z', '+00:00')
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Normalise to UTC
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _fetch_events(limit=20):
    now_ts  = time.time()
    utc_now = datetime.now(timezone.utc)

    if _cache['data'] is not None and (now_ts - _cache['ts']) < CACHE_TTL:
        return _cache['data']
    try:
        resp = http.get(HC_API, params={
            'endsAfter':        utc_now.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'orderByField':     'startsOn',
            'orderByDirection': 'ascending',
            'status':           'Approved',
            'limit':            limit * 3,   # fetch extra; we'll filter client-side
            'skip':             0,
        }, timeout=8)
        resp.raise_for_status()

        events = []
        for e in resp.json().get('value', []):
            starts_raw = e.get('startsOn', '')
            starts_dt  = _parse_dt(starts_raw)

            # Hard client-side filter — skip anything that started in the past
            if starts_dt and starts_dt <= utc_now:
                continue

            date_str, time_str = _fmt_dt(starts_raw)
            events.append({
                'id':         e.get('id'),
                'name':       e.get('name', 'Untitled'),
                'org':        e.get('organizationName', ''),
                'location':   e.get('location') or 'SCSU Campus',
                'date':       date_str,
                'time':       time_str,
                'theme':      e.get('theme', ''),
                'categories': e.get('categoryNames', []),
                'benefits':   e.get('benefitNames', []),
                'rsvp':       e.get('rsvpTotal', 0),
                'img':        _img(e.get('imagePath')),
                'blurb':      _strip_html(e.get('description', '')),
                'url':        f"{HC_BASE}/event/{e.get('id')}",
            })
            if len(events) >= limit:
                break

        _cache['data'] = events
        _cache['ts']   = now_ts
        return events
    except Exception:
        return None


def _fetch_news(limit=4):
    now = time.time()
    if _news_cache['data'] and (now - _news_cache['ts']) < CACHE_TTL:
        return _news_cache['data']
    try:
        resp = http.get(HC_NEWS, params={
            'orderByField': 'publishedOn',
            'orderByDirection': 'descending',
            'status': 'Approved',
            'limit': limit,
            'skip': 0,
        }, timeout=6)
        resp.raise_for_status()
        news = []
        for n in resp.json().get('value', []):
            date_str, _ = _fmt_dt(n.get('publishedOn', '') or n.get('createdOn', ''))
            news.append({
                'id':    n.get('id'),
                'title': n.get('title') or n.get('headline', 'Untitled'),
                'org':   n.get('organizationName', ''),
                'date':  date_str,
                'img':   _img(n.get('imagePath'), preset='medium-sq'),
                'blurb': _strip_html(n.get('summary') or n.get('body', ''))[:100],
                'url':   f"{HC_BASE}/news/{n.get('id')}",
            })
        _news_cache['data'] = news
        _news_cache['ts']   = now
        return news
    except Exception:
        return []


def _fetch_orgs(limit=6):
    now = time.time()
    if _orgs_cache['data'] and (now - _orgs_cache['ts']) < CACHE_TTL:
        return _orgs_cache['data']
    try:
        resp = http.get(HC_ORGS, params={
            'orderByField': 'name',
            'orderByDirection': 'ascending',
            'status': 'Active',
            'limit': limit,
            'skip': 0,
        }, timeout=6)
        resp.raise_for_status()
        orgs = []
        for o in resp.json().get('value', []):
            orgs.append({
                'id':   o.get('id'),
                'name': o.get('name', ''),
                'img':  _img(o.get('profilePicture'), preset='small-sq'),
                'url':  f"{HC_BASE}/organization/{o.get('websiteKey') or o.get('id')}",
            })
        _orgs_cache['data'] = orgs
        _orgs_cache['ts']   = now
        return orgs
    except Exception:
        return []


@events_bp.route('/')
@login_required
def index():
    theme  = request.args.get('theme', '')
    events = _fetch_events(limit=30)
    if events and theme:
        events = [e for e in events if e['theme'].lower() == theme.lower()]
    error  = events is None
    themes = ['Social', 'ThoughtfulLearning', 'Arts', 'Spirituality',
              'CommunityService', 'Fundraising', 'Cultural']
    return render_template('events/index.html', events=events or [],
                           error=error, theme=theme, themes=themes,
                           active_page=None)


@events_bp.route('/<int:event_id>')
@login_required
def detail(event_id):
    return render_template('events/detail.html',
                           event={'id': event_id, 'title': '', 'type': '',
                                  'description': '', 'date': '', 'time': '',
                                  'location': '', 'post_count': 0, 'rsvp_count': 0},
                           active_page=None)
