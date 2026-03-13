from flask import Flask
from flask_login import LoginManager
from config import Config
from app.models import db, User
from app.utils import timeago, inject_globals
from app.blueprints.main import main_bp
from app.blueprints.auth import auth_bp
from app.blueprints.posts import posts_bp
from app.blueprints.profile import profile_bp
from app.blueprints.notifications import notifications_bp
from app.blueprints.messages import messages_bp
from app.blueprints.bookmarks import bookmarks_bp
from app.blueprints.settings import settings_bp
from app.blueprints.follow import follow_bp
from app.blueprints.forum import forum_bp
from app.blueprints.resources import resources_bp
from app.blueprints.classes import classes_bp
from app.blueprints.groups import groups_bp
from app.blueprints.events import events_bp
from app.blueprints.errors import errors_bp

login_manager = LoginManager()


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please sign in to access Agora.'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Auto-create any missing tables (safe for new models on Railway)
    with app.app_context():
        db.create_all()

    # Template filters & globals
    app.jinja_env.filters['timeago'] = timeago
    app.context_processor(inject_globals)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(bookmarks_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(follow_bp)
    app.register_blueprint(forum_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(classes_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(errors_bp)

    # CLI: flask init-db  ->  creates all tables + seeds SCSU courses
    @app.cli.command('init-db')
    def init_db():
        db.create_all()
        _seed_courses()
        print('Database initialized and courses seeded.')

    return app


def _seed_courses():
    from app.models import Course
    courses = [
        ('CSCI 101', 'Introduction to Computer Science'),
        ('CSCI 201', 'Introduction to Programming'),
        ('CSCI 301', 'Data Structures'),
        ('CSCI 351', 'Data Structures & Algorithms'),
        ('CSCI 411', 'Database Systems'),
        ('CSCI 421', 'Operating Systems'),
        ('CSCI 431', 'Computer Networks'),
        ('CSCI 441', 'Software Engineering'),
        ('CSCI 461', 'Theory of Computation'),
        ('MATH 112', 'College Algebra'),
        ('MATH 191', 'Calculus I'),
        ('MATH 192', 'Calculus II'),
        ('MATH 221', 'Linear Algebra'),
        ('MATH 361', 'Probability and Statistics'),
        ('BIOL 151', 'General Biology I'),
        ('ENGL 191', 'Composition'),
        ('PSYC 101', 'Introduction to Psychology'),
        ('ECON 206', 'Principles of Economics'),
    ]
    for code, name in courses:
        if not Course.query.filter_by(code=code).first():
            db.session.add(Course(code=code, name=name))
    db.session.commit()
