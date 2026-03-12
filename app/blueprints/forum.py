from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user
from app.models import db, Problem, Answer, Course, Tag, UpvoteOnProblem, \
                       UpvoteOnAnswer, Notification, Enrollment

forum_bp = Blueprint('forum', __name__, url_prefix='/forum')


@forum_bp.route('/')
@login_required
def index():
    tab       = request.args.get('tab', 'all')
    course_id = request.args.get('course_id', type=int)

    q = Problem.query
    if course_id:
        q = q.filter_by(course_id=course_id)
    problems = q.order_by(Problem.created_at.desc()).limit(50).all()

    # Attach per-user upvote flag
    upvoted_ids = {u.problem_id for u in
                   UpvoteOnProblem.query.filter_by(user_id=current_user.id).all()}
    for p in problems:
        p.is_upvoted_by_me = p.id in upvoted_ids

    enrolled = (Enrollment.query.filter_by(user_id=current_user.id)
                .join(Course).all())
    courses = [e.course for e in enrolled]

    return render_template('forum/index.html', problems=problems,
                           courses=courses, active_page=None)


@forum_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        course_id   = request.form.get('course_id', type=int)
        tag_str     = request.form.get('tags', '')

        if not title or not description or not course_id:
            enrolled = (Enrollment.query.filter_by(user_id=current_user.id)
                        .join(Course).all())
            courses = [e.course for e in enrolled]
            return render_template('forum/create.html',
                                   error='Title, description, and course are required.',
                                   courses=courses, active_page=None)

        problem = Problem(user_id=current_user.id, course_id=course_id,
                          title=title, description=description)
        for raw in tag_str.split(','):
            name = raw.strip().lower().lstrip('#')
            if name:
                tag = Tag.query.filter_by(name=name).first() or Tag(name=name)
                problem._tags.append(tag)

        db.session.add(problem)
        db.session.commit()
        return redirect(url_for('forum.detail', problem_id=problem.id))

    enrolled = (Enrollment.query.filter_by(user_id=current_user.id)
                .join(Course).all())
    courses = [e.course for e in enrolled]
    return render_template('forum/create.html', courses=courses, active_page=None)


@forum_bp.route('/<int:problem_id>')
@login_required
def detail(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    upvoted = UpvoteOnProblem.query.filter_by(
        problem_id=problem_id, user_id=current_user.id).first() is not None
    problem.is_upvoted_by_me = upvoted

    answers = (problem.answers
               .order_by(Answer.is_accepted.desc(), Answer.created_at.asc()).all())
    answer_upvoted_ids = {u.answer_id for u in
                          UpvoteOnAnswer.query.filter_by(user_id=current_user.id).all()}
    for a in answers:
        a.is_upvoted_by_me = a.id in answer_upvoted_ids

    return render_template('forum/detail.html', problem=problem,
                           answers=answers, active_page=None)


@forum_bp.route('/<int:problem_id>/upvote', methods=['POST'])
@login_required
def upvote_problem(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    existing = UpvoteOnProblem.query.filter_by(
        problem_id=problem_id, user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(UpvoteOnProblem(problem_id=problem_id,
                                       user_id=current_user.id))
    db.session.commit()
    return redirect(request.referrer or url_for('forum.index'))


@forum_bp.route('/<int:problem_id>/answer', methods=['POST'])
@login_required
def answer(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    content = request.form.get('content', '').strip()
    if content:
        ans = Answer(problem_id=problem_id, user_id=current_user.id, content=content)
        db.session.add(ans)
        if problem.user_id != current_user.id:
            db.session.add(Notification(
                recipient_id=problem.user_id,
                actor_id=current_user.id,
                type='answer',
            ))
        db.session.commit()
    return redirect(url_for('forum.detail', problem_id=problem_id))


@forum_bp.route('/answer/<int:answer_id>/accept', methods=['POST'])
@login_required
def accept_answer(answer_id):
    ans = Answer.query.get_or_404(answer_id)
    if ans.problem.user_id != current_user.id:
        abort(403)
    # Toggle: unaccept all others first
    for a in ans.problem.answers:
        a.is_accepted = False
    ans.is_accepted = True
    db.session.commit()
    return redirect(url_for('forum.detail', problem_id=ans.problem_id))


@forum_bp.route('/answer/<int:answer_id>/upvote', methods=['POST'])
@login_required
def upvote_answer(answer_id):
    Answer.query.get_or_404(answer_id)
    existing = UpvoteOnAnswer.query.filter_by(answer_id=answer_id,
                                              user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(UpvoteOnAnswer(answer_id=answer_id, user_id=current_user.id))
    db.session.commit()
    return redirect(request.referrer or url_for('forum.index'))
