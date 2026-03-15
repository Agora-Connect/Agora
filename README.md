# Agora

Academic collaboration platform for St. Cloud State University students — a private, university-only space to ask questions, share resources, and connect with classmates.

**Live:** [agora-production.up.railway.app](https://agora-production.up.railway.app)

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
| Database | PostgreSQL (Railway) via SQLAlchemy ORM |
| Auth | Flask-Login + Werkzeug password hashing |
| Styling | Tailwind CSS (CDN, no build step) + Heroicons (inline SVG) |
| Images | Pillow — server-side resize before base64 storage |
| Campus data | Huskies Connect Presence API (events, news, orgs) |
| Deployment | Railway (Flask + PostgreSQL, Gunicorn) |

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
│   ├── auth/               # login.html, register.html
│   ├── feed/               # home feed
│   ├── forum/              # Q&A templates
│   ├── profile/            # view.html, edit.html
│   ├── groups/             # index, detail, private (join request)
│   ├── events/             # Events listing
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
- 15-minute server-side cache; fully automatic — no manual updates needed

### Profile
- Avatar and banner photo upload (Pillow resizing, stored as base64 in PostgreSQL)
- Bio, major, academic year
- Reputation score displayed on profile

---

## Running Locally

```bash
# 1. Clone and create a virtual environment
git clone https://github.com/Agora-Connect/Agora.git
cd Agora
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
cp .env.example .env
# Edit .env — set DATABASE_URL and SECRET_KEY

# 4. Run
flask run
```

The app will be available at `http://localhost:5000`.

**Required environment variables:**

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (e.g. `postgresql://user:pass@host/db`) |
| `SECRET_KEY` | Flask session secret (any random string for dev) |

---

## Deployment (Railway)

The app is configured for one-click Railway deployment:

- `Procfile` runs Gunicorn: `web: gunicorn run:app`
- `runtime.txt` pins the Python version
- `nixpacks.toml` controls the build environment
- Database tables are auto-created at startup via `db.create_all()` inside `create_app()`
- Schema migrations (e.g. column type changes) are applied at startup via `db.engine.execute()`

Set `DATABASE_URL` and `SECRET_KEY` as Railway environment variables.

---

## Data Models

Core SQLAlchemy models in `app/models.py`:

| Model | Description |
|-------|-------------|
| `User` | Student account — display name, avatar, reputation, major, year |
| `Post` | Feed post with optional anonymity and repost support |
| `Problem` | Forum question linked to a course |
| `Answer` | Answer to a Problem; one can be marked accepted |
| `Resource` | Shared academic material with borrow workflow |
| `Course` | University course (e.g. CSCI 411) |
| `Enrollment` | M:N junction — User ↔ Course |
| `Group` / `GroupMembership` | Study groups with membership, invitations, join requests |
| `Follow` | Self-referential social graph |
| `Notification` | Unified notification model (likes, follows, answers, invites) |
| `Message` | Direct messages between users |
| `Bookmark` | Saved posts |
| `Repost` | Repost tracking |

---

## Organization

This repository is part of the [Agora-Connect](https://github.com/Agora-Connect) GitHub organization:

| Repository | Purpose |
|-----------|---------|
| [Agora](https://github.com/Agora-Connect/Agora) | **This repo** — production Flask application |
| [docs](https://github.com/Agora-Connect/docs) | Design documents, ER diagrams, domain specification |
| [backend](https://github.com/Agora-Connect/backend) | Early prototype (reference only, not production) |
| [database](https://github.com/Agora-Connect/database) | Early SQLite prototype queries (reference only) |

---

## License

MIT License — see [LICENSE](./LICENSE) for details.
