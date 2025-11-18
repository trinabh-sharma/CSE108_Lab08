from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user

from extensions import db
from models import Course, Enrollment
from decorators import roles_required, owns_course_or_admin

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


@teacher_bp.route("/")
@login_required
@roles_required("teacher", "admin")
def dashboard():
    if current_user.role == "admin":
        courses = Course.query.order_by(Course.code).all()
    else:
        courses = Course.query.filter_by(teacher_id=current_user.id).order_by(Course.code).all()
    return render_template("teacher_dashboard.html", courses=courses)


@teacher_bp.route("/course/<int:course_id>")
@login_required
@roles_required("teacher", "admin")
def course(course_id: int):
    if not owns_course_or_admin(course_id):
        abort(403)

    course = Course.query.get_or_404(course_id)
    roster = Enrollment.query.filter_by(course_id=course_id).all()
    return render_template("teacher_course.html", course=course, roster=roster)


@teacher_bp.route("/course/<int:course_id>/grade", methods=["POST"])
@login_required
@roles_required("teacher", "admin")
def update_grade(course_id: int):
    if not owns_course_or_admin(course_id):
        abort(403)

    student_id = int(request.form["student_id"])
    grade = request.form.get("grade", "").strip()

    enrollment = Enrollment.query.filter_by(
        course_id=course_id, student_id=student_id
    ).first_or_404()
    enrollment.grade = grade or None
    db.session.commit()

    flash("Grade updated.", "success")
    return redirect(url_for("teacher.course", course_id=course_id))
