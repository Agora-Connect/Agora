# Agora

Academic collaboration platform for St. Cloud State University students — a private, university-only space to ask questions, share resources, and connect with classmates.

**Live:** [web-production-48b9b.up.railway.app](https://web-production-48b9b.up.railway.app)

---

## What is Agora?

Agora is a campus-exclusive social platform restricted to verified SCSU students (`@stcloudstate.edu` emails). It replaces the scattered use of Discord, GroupMe, and Reddit for academic help by providing one unified space with:

- A **Questions Forum** for course-specific Q&A with accepted answers and reputation scoring
- A **Resource Hub** for sharing textbooks, notes, and study materials
- **Study Groups** with public/private membership and invite workflows
- **Class Pages** for course-scoped discussion
- **Campus Events** pulled live from Huskies Connect (SCSU's event platform)
- A **social feed** with posts, reposts, bookmarks, and following

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | Flask 3.0 (Jinja2 templates, Blueprint routing) |
| Database | MySQL — designed and managed by the team, hosted on Railway |
| ORM | SQLAlchemy + PyMySQL |
| Auth | Flask-Login + Werkzeug password hashing |
| Styling | Tailwind CSS (CDN, no build step) + Heroicons (inline SVG) |
| Images | Pillow — server-side resize before base64 storage |
| Campus data | Huskies Connect Presence API (events, news, orgs) |
| Deployment | Railway (Flask + MySQL, Gunicorn) |

---

## Project Structure

```
agora/
├── run.py                  # App entry point
├── config.py               # Config (env vars, DB URI)
├── requirements.txt
├── Procfile                # Railway: gunicorn run:app
├── app/
│   ├── __init__.py         # create_app(), blueprints, context processors
│   ├── models.py           # All SQLAlchemy models
│   ├── utils.py            # Helpers: timeago, inject_globals, enrich_posts
│   └── blueprints/
│       ├── auth.py         # Register, login, logout (SCSU email gate)
│       ├── main.py         # Home feed
│       ├── posts.py        # Create, like, repost, bookmark posts
│       ├── profile.py      # View + edit profile, avatar/banner upload
│       ├── forum.py        # Q&A forum — problems, answers, accepted answers
│       ├── resources.py    # Resource sharing + borrow requests
│       ├── classes.py      # Class pages + enrollment
│       ├── groups.py       # Study groups (public/private, invites, requests)
│       ├── events.py       # Huskies Connect integration (events, news, orgs)
│       ├── messages.py     # Direct messages
│       ├── notifications.py# Notification feed
│       ├── bookmarks.py    # Saved posts
│       ├── follow.py       # Follow/unfollow users
│       └── settings.py     # Account settings
├── templates/
│   ├── base.html           # Root layout with sidebar navigation
│   ├── components/         # right_sidebar.html, post_card.html, etc.
│   └── ...
└── static/
    └── css/styles.css
```

---

## Key Features

### Authentication
- Registration restricted to `@stcloudstate.edu` email addresses
- Password hashing via Werkzeug; session management via Flask-Login

### Questions Forum
- Post academic questions; multiple users can answer
- Question author marks one answer as accepted
- Upvotes on questions and answers contribute to user reputation

### Resource Sharing
- Upload references to textbooks, notes, past exams
- Borrow request workflow (pending → approved/declined)

### Study Groups
- Public groups (join instantly) or private groups (request to join)
- Admin invites members by `@username`
- Single admin per group; admin transfer and auto-promotion on admin leave

### Campus Events Sidebar
- Live data from Huskies Connect — upcoming events with images, dates, locations
- Campus news and student organizations from the same API
- 15-minute server-side cache; fully automatic

### Profile
- Avatar and banner photo upload (Pillow resizing, stored as base64 in MySQL)
- Bio, major, academic year
- Reputation score displayed on profile

---

## Running Locally

```bash
git clone https://github.com/Agora-Connect/Agora.git
cd Agora
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# create a .env file with DATABASE_URL and SECRET_KEY
flask run
```

**Required environment variables:**

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | MySQL connection string (`mysql://user:pass@host:port/db`) |
| `SECRET_KEY` | Flask session secret |

---

## Deployment (Railway)

- `Procfile` runs Gunicorn: `web: gunicorn run:app`
- `runtime.txt` pins the Python version
- Database tables are auto-created at startup via `db.create_all()`
- Set `DATABASE_URL` and `SECRET_KEY` as Railway environment variables

---

## Database

The MySQL database schema is fully designed and maintained by the team. See the [database](https://github.com/Agora-Connect/database) repository for the complete schema, queries, indexes, transactions, and application scripts.

---

## Organization

| Repository | Purpose |
|-----------|---------|
| [Agora](https://github.com/Agora-Connect/Agora) | **This repo** — production Flask application |
| [database](https://github.com/Agora-Connect/database) | MySQL schema, queries, indexes, transactions, MongoDB component |
| [docs](https://github.com/Agora-Connect/docs) | Design documents, ER diagram, normalization, domain specification |

---

## License

MIT License — see [LICENSE](./LICENSE) for details.
