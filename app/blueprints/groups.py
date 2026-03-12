from flask import Blueprint, render_template
from flask_login import login_required

groups_bp = Blueprint('groups', __name__, url_prefix='/groups')


@groups_bp.route('/')
@login_required
def index():
    # Groups feature coming soon - no hardcoded data
    groups = []
    return render_template('groups/index.html', groups=groups, active_page=None)
