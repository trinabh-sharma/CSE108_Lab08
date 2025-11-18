from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint

from extensions import db

from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # "student", "teacher", "admin"

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=30)

    teacher_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    teacher = db.relationship("User", foreign_keys=[teacher_id])


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

    grade = db.Column(db.String(5))

    student = db.relationship("User", foreign_keys=[student_id])
    course = db.relationship("Course", foreign_keys=[course_id])

    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course"),
    )
