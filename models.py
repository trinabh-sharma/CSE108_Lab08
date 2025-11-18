from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db, login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=30)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher = db.relationship('User', foreign_keys=[teacher_id])


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.String(5))
    student = db.relationship('User', foreign_keys=[student_id])
    course = db.relationship('Course', foreign_keys=[course_id])
    __table_args__ = (UniqueConstraint('student_id', 'course_id', name='uq_student_course'),)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) if user_id else None


def seed():
    """Populate the database with an initial set of users and courses."""
    db.create_all()
    if User.query.first():
        return

    admin = User(username='admin', role='admin')
    admin.set_password('admin')

    t1 = User(username='turing', role='teacher')
    t1.set_password('teacher')
    t2 = User(username='hopper', role='teacher')
    t2.set_password('teacher')

    s1 = User(username='alice', role='student')
    s1.set_password('student')
    s2 = User(username='bob', role='student')
    s2.set_password('student')
    s3 = User(username='charlie', role='student')
    s3.set_password('student')

    db.session.add_all([admin, t1, t2, s1, s2, s3])
    db.session.flush()

    c1 = Course(code='CS101', title='Intro to CS', capacity=2, teacher_id=t1.id)
    c2 = Course(code='CS201', title='Data Structures', capacity=3, teacher_id=t1.id)
    c3 = Course(code='MTH100', title='Calculus I', capacity=2, teacher_id=t2.id)
    db.session.add_all([c1, c2, c3])
    db.session.commit()
