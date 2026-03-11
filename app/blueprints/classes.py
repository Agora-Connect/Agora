from flask import Blueprint, render_template
from app.mock_data import COURSES, POSTS

classes_bp = Blueprint('classes', __name__, url_prefix='/classes')


@classes_bp.route('/')
def index():
    enrolled = [c for c in COURSES if c['enrolled']]
    return render_template('classes/index.html', courses=COURSES,
                           enrolled=enrolled, active_page=None)


@classes_bp.route('/<int:course_id>')
def detail(course_id):
    course = next((c for c in COURSES if c['id'] == course_id), COURSES[0])
    course_posts = [p for p in POSTS if p['course']['id'] == course_id]
    return render_template('classes/detail.html', course=course,
                           posts=course_posts, active_page=None)
