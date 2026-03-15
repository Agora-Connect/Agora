from datetime import datetime, timezone
from flask_login import current_user


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
    notification_count = 0
    has_unread_messages = False

    sidebar_events = []
    if current_user.is_authenticated:
        from app.models import Notification, Message
        notification_count = Notification.query.filter_by(
            recipient_id=current_user.id, is_read=False
        ).count()
        has_unread_messages = Message.query.filter_by(
            recipient_id=current_user.id, is_read=False
        ).count() > 0
        from app.blueprints.events import _fetch_events
        sidebar_events = (_fetch_events(limit=5) or [])[:5]

    return {
        'notification_count': notification_count,
        'has_unread_messages': has_unread_messages,
        'sidebar_events': sidebar_events,
    }


def enrich_posts(posts, user_id):
    """Attach per-user boolean flags to a list of Post objects."""
    from app.models import UpvoteOnPost, Repost, Bookmark

    if not user_id or not posts:
        for p in posts:
            p.is_liked_by_me = False
            p.is_reposted_by_me = False
            p.is_bookmarked_by_me = False
        return posts

    post_ids = [p.id for p in posts]
    liked     = {r.post_id for r in UpvoteOnPost.query.filter(
                    UpvoteOnPost.user_id == user_id,
                    UpvoteOnPost.post_id.in_(post_ids)).all()}
    reposted  = {r.post_id for r in Repost.query.filter(
                    Repost.user_id == user_id,
                    Repost.post_id.in_(post_ids)).all()}
    bookmarked = {r.post_id for r in Bookmark.query.filter(
                    Bookmark.user_id == user_id,
                    Bookmark.post_id.in_(post_ids)).all()}

    for p in posts:
        p.is_liked_by_me      = p.id in liked
        p.is_reposted_by_me   = p.id in reposted
        p.is_bookmarked_by_me = p.id in bookmarked

    return posts
