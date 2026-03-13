import os
import sys
from app import create_app, _seed_courses
from app.models import db

app = create_app()

with app.app_context():
    db_url = os.environ.get('DATABASE_URL', 'NOT SET')
    print(f"[startup] DATABASE_URL = {db_url[:40]}...", flush=True)
    try:
        db.create_all()
        print("[startup] db.create_all() OK", flush=True)
        _seed_courses()
        print("[startup] _seed_courses() OK", flush=True)
    except Exception as e:
        print(f"[startup] ERROR: {e}", file=sys.stderr, flush=True)

if __name__ == '__main__':
    app.run(debug=False)
