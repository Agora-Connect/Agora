from flask import Flask
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


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.secret_key = 'agora-dev-secret-key'

    # Register template filters
    app.jinja_env.filters['timeago'] = timeago

    # Inject globals into every template
    app.context_processor(inject_globals)

    # Register blueprints
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

    return app
