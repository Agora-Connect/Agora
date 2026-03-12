from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ── Junction tables ──────────────────────────────────────────────────────────

post_tags = db.Table(
    'post_tag',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id',  db.Integer, db.ForeignKey('tag.id'),  primary_key=True),
)

problem_tags = db.Table(
    'problem_tag',
    db.Column('problem_id', db.Integer, db.ForeignKey('problem.id'), primary_key=True),
    db.Column('tag_id',     db.Integer, db.ForeignKey('tag.id'),     primary_key=True),
)


# ── User ─────────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id               = db.Column(db.Integer, primary_key=True)
    email            = db.Column(db.String(255), unique=True, nullable=False)
    username         = db.Column(db.String(50),  unique=True, nullable=False)
    name             = db.Column(db.String(255), nullable=False)
    password_hash    = db.Column(db.String(255), nullable=False)
    university       = db.Column(db.String(255), default='Saint Cloud State University')
    major            = db.Column(db.String(255))
    year             = db.Column(db.String(50))
    bio              = db.Column(db.Text)
    avatar_url       = db.Column(db.String(500))
    banner_url       = db.Column(db.String(500))
    reputation_score = db.Column(db.Integer, default=0)
    is_verified      = db.Column(db.Boolean, default=False)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    posts     = db.relationship('Post',     foreign_keys='Post.user_id',     backref='author', lazy='dynamic')
    problems  = db.relationship('Problem',  foreign_keys='Problem.user_id',  backref='author', lazy='dynamic')
    answers   = db.relationship('Answer',   foreign_keys='Answer.user_id',   backref='author', lazy='dynamic')
    resources = db.relationship('Resource', foreign_keys='Resource.user_id', backref='owner',  lazy='dynamic')

    following   = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy='dynamic')
    followers   = db.relationship('Follow', foreign_keys='Follow.followed_id', backref='followed', lazy='dynamic')
    bookmarks   = db.relationship('Bookmark', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', foreign_keys='Notification.recipient_id',
                                    backref='recipient', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def display_name(self):
        return self.name

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()


# ── Course ───────────────────────────────────────────────────────────────────

class Course(db.Model):
    __tablename__ = 'course'

    id          = db.Column(db.Integer, primary_key=True)
    code        = db.Column(db.String(50),  unique=True, nullable=False)
    name        = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    posts       = db.relationship('Post',       backref='course', lazy='dynamic')
    problems    = db.relationship('Problem',    backref='course', lazy='dynamic')
    resources   = db.relationship('Resource',  backref='course', lazy='dynamic')
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic')


# ── Enrollment ───────────────────────────────────────────────────────────────

class Enrollment(db.Model):
    __tablename__ = 'enrollment'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'),   nullable=False)
    course_id   = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')


# ── Tag ──────────────────────────────────────────────────────────────────────

class Tag(db.Model):
    __tablename__ = 'tag'

    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __str__(self):
        return self.name


# ── Post ─────────────────────────────────────────────────────────────────────

class Post(db.Model):
    __tablename__ = 'post'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'),   nullable=False)
    course_id    = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)
    content      = db.Column(db.Text, nullable=False)
    image_url    = db.Column(db.String(500))
    is_anonymous = db.Column(db.Boolean, default=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    _tags       = db.relationship('Tag', secondary=post_tags, lazy='subquery')
    comments    = db.relationship('CommentOnPost', backref='post', lazy='dynamic',
                                  cascade='all, delete-orphan')
    likes       = db.relationship('UpvoteOnPost', backref='post', lazy='dynamic',
                                  cascade='all, delete-orphan')
    bookmarks_rel = db.relationship('Bookmark', backref='post', lazy='dynamic',
                                    cascade='all, delete-orphan')
    reposts     = db.relationship('Repost', backref='post', lazy='dynamic',
                                  cascade='all, delete-orphan')

    @property
    def tags(self):
        return [t.name for t in self._tags]

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def reply_count(self):
        return self.comments.count()

    @property
    def repost_count(self):
        return self.reposts.count()


# ── CommentOnPost ─────────────────────────────────────────────────────────────

class CommentOnPost(db.Model):
    __tablename__ = 'comment_on_post'

    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('post.id'),  nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    comment_author = db.relationship('User')


# ── UpvoteOnPost ──────────────────────────────────────────────────────────────

class UpvoteOnPost(db.Model):
    __tablename__ = 'upvote_on_post'

    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ── Bookmark ──────────────────────────────────────────────────────────────────

class Bookmark(db.Model):
    __tablename__ = 'bookmark'

    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ── Repost ────────────────────────────────────────────────────────────────────

class Repost(db.Model):
    __tablename__ = 'repost'

    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ── Follow ────────────────────────────────────────────────────────────────────

class Follow(db.Model):
    __tablename__ = 'follow'

    id          = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)


# ── Notification ──────────────────────────────────────────────────────────────

class Notification(db.Model):
    __tablename__ = 'notification'

    id           = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    actor_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type         = db.Column(db.String(50), nullable=False)  # like/follow/reply/repost/answer
    post_id      = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    is_read      = db.Column(db.Boolean, default=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    actor = db.relationship('User', foreign_keys=[actor_id])
    post  = db.relationship('Post')


# ── Problem ───────────────────────────────────────────────────────────────────

class Problem(db.Model):
    __tablename__ = 'problem'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'),   nullable=False)
    course_id   = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title       = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    _tags   = db.relationship('Tag', secondary=problem_tags, lazy='subquery')
    answers = db.relationship('Answer', backref='problem', lazy='dynamic',
                               cascade='all, delete-orphan')
    upvotes = db.relationship('UpvoteOnProblem', backref='problem', lazy='dynamic',
                               cascade='all, delete-orphan')

    @property
    def tags(self):
        return [t.name for t in self._tags]

    @property
    def answer_count(self):
        return self.answers.count()

    @property
    def has_accepted_answer(self):
        return self.answers.filter_by(is_accepted=True).first() is not None

    @property
    def upvote_count(self):
        return self.upvotes.count()


# ── Answer ────────────────────────────────────────────────────────────────────

class Answer(db.Model):
    __tablename__ = 'answer'

    id          = db.Column(db.Integer, primary_key=True)
    problem_id  = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'),    nullable=False)
    content     = db.Column(db.Text, nullable=False)
    is_accepted = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    upvotes = db.relationship('UpvoteOnAnswer', backref='answer', lazy='dynamic',
                               cascade='all, delete-orphan')

    @property
    def upvote_count(self):
        return self.upvotes.count()


# ── UpvoteOnProblem ───────────────────────────────────────────────────────────

class UpvoteOnProblem(db.Model):
    __tablename__ = 'upvote_on_problem'

    id         = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),    nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ── UpvoteOnAnswer ────────────────────────────────────────────────────────────

class UpvoteOnAnswer(db.Model):
    __tablename__ = 'upvote_on_answer'

    id         = db.Column(db.Integer, primary_key=True)
    answer_id  = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),   nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ── Resource ──────────────────────────────────────────────────────────────────

class Resource(db.Model):
    __tablename__ = 'resource'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'),   nullable=False)
    course_id   = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title       = db.Column(db.String(255), nullable=False)
    type        = db.Column(db.String(50),  nullable=False)
    description = db.Column(db.Text)
    available   = db.Column(db.Boolean, default=True)
    file_path   = db.Column(db.String(500))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    borrow_requests = db.relationship('BorrowRequest', backref='resource', lazy='dynamic',
                                       cascade='all, delete-orphan')


# ── BorrowRequest ─────────────────────────────────────────────────────────────

class BorrowRequest(db.Model):
    __tablename__ = 'borrow_request'

    id           = db.Column(db.Integer, primary_key=True)
    resource_id  = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'),     nullable=False)
    owner_id     = db.Column(db.Integer, db.ForeignKey('user.id'),     nullable=False)
    status       = db.Column(db.String(50), nullable=False, default='pending')
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requester = db.relationship('User', foreign_keys=[requester_id])
    owner     = db.relationship('User', foreign_keys=[owner_id])


# ── Message ───────────────────────────────────────────────────────────────────

class Message(db.Model):
    __tablename__ = 'message'

    id           = db.Column(db.Integer, primary_key=True)
    sender_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content      = db.Column(db.Text, nullable=False)
    sent_at      = db.Column(db.DateTime, default=datetime.utcnow)
    is_read      = db.Column(db.Boolean, default=False)

    sender    = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])
