from datetime import datetime, timezone
from app.mock_data import CURRENT_USER


def timeago(dt):
    """Convert datetime to relative time string."""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return 'now'
    elif seconds < 3600:
        return f'{seconds // 60}m'
    elif seconds < 86400:
        return f'{seconds // 3600}h'
    elif seconds < 604800:
        return f'{seconds // 86400}d'
    else:
        return dt.strftime('%b %-d')


def inject_globals():
    """Inject variables available in every template."""
    return {
        'current_user': CURRENT_USER,
        'notification_count': 4,
        'has_unread_messages': True,
    }
