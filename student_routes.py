from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import func

from extensions import db
from models import Course, Enrollment
from decorators import roles_required

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/my-classes")
@login_required
@roles_required("student")
def my_classes():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    return render_template("student_my_classes.html", enrollments=enrollments)


@student_bp.route("/all-classes")
@login_required
@roles_required("student")
def all_classes():
    courses = Course.query.order_by(Course.code).all()
    counts = dict(
        db.session.query(Enrollment.course_id, func.count(Enrollment.id))
        .group_by(Enrollment.course_id)
        .all()
    )
    return render_template("student_all_classes.html", courses=courses, counts=counts)


@student_bp.route("/enroll/<int:course_id>", methods=["POST"])
@login_required
@roles_required("student")
def enroll(course_id: int):
    course = Course.query.get_or_404(course_id)

    existing = Enrollment.query.filter_by(
        student_id=current_user.id, course_id=course_id
    ).first()
    if existing:
        flash("You are already enrolled in this class.", "warning")
        return redirect(url_for("student.all_classes"))

    current_count = Enrollment.query.filter_by(course_id=course_id).count()
    if current_count >= course.capacity:
        flash("This class is full.", "error")
        return redirect(url_for("student.all_classes"))

    enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()

    flash("Enrolled successfully.", "success")
    return redirect(url_for("student.my_classes"))
