from flask import Blueprint, render_template
from app.mock_data import PROBLEMS, COURSES

forum_bp = Blueprint('forum', __name__, url_prefix='/forum')


@forum_bp.route('/')
def index():
    return render_template('forum/index.html', problems=PROBLEMS,
                           courses=COURSES, active_page=None)


@forum_bp.route('/<int:problem_id>')
def detail(problem_id):
    problem = next((p for p in PROBLEMS if p['id'] == problem_id), PROBLEMS[0])
    return render_template('forum/detail.html', problem=problem, active_page=None)
