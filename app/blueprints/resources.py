from flask import Blueprint, render_template
from app.mock_data import RESOURCES, COURSES

resources_bp = Blueprint('resources', __name__, url_prefix='/resources')


@resources_bp.route('/')
def index():
    return render_template('resources/index.html', resources=RESOURCES,
                           courses=COURSES, active_page=None)
