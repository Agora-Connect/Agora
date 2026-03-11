from flask import Blueprint, render_template

groups_bp = Blueprint('groups', __name__, url_prefix='/groups')

GROUPS = [
    {'id': 1, 'name': 'CSCI 411 Study Group', 'members': 24, 'description': 'Database systems study group'},
    {'id': 2, 'name': 'UW Hackathon Team', 'members': 8, 'description': 'Preparing for Hackathon 2026'},
    {'id': 3, 'name': 'Math 221 Help Desk', 'members': 31, 'description': 'Linear algebra mutual aid'},
]


@groups_bp.route('/')
def index():
    return render_template('groups/index.html', groups=GROUPS, active_page=None)
