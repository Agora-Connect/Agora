from app import create_app, _seed_courses
from app.models import db

app = create_app()

with app.app_context():
    db.create_all()
    _seed_courses()

if __name__ == '__main__':
    app.run(debug=False)
