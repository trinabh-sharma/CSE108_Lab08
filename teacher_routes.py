from flask import Blueprint, render_template, abort, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func

from decorators import roles_required, owns_course_or_admin
from extensions import db
from models import Course, Enrollment

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')


@teacher_bp.route('/')
@teacher_bp.route('')
@login_required
@roles_required('teacher')
def dashboard():
    courses = Course.query.filter_by(teacher_id=current_user.id).order_by(Course.code).all()
    # Get enrollment counts for each course
    counts = dict(
        db.session.query(Enrollment.course_id, func.count(Enrollment.id))
        .group_by(Enrollment.course_id)
        .all()
    )
    return render_template('teacher_dashboard.html', courses=courses, counts=counts)


@teacher_bp.route('/course/<int:course_id>')
@login_required
@roles_required('teacher', 'admin')
def course(course_id):
    if not owns_course_or_admin(course_id):
        abort(403)
    course_obj = Course.query.get_or_404(course_id)
    roster = Enrollment.query.filter_by(course_id=course_id).all()
    return render_template('teacher_course.html', course=course_obj, roster=roster)


@teacher_bp.route('/course/<int:course_id>/grade', methods=['POST'])
@login_required
@roles_required('teacher', 'admin')
def grade(course_id):
    if not owns_course_or_admin(course_id):
        abort(403)
    student_id = int(request.form['student_id'])
    grade_value = request.form.get('grade', '').strip() or None
    enrollment = Enrollment.query.filter_by(course_id=course_id, student_id=student_id).first_or_404()
    enrollment.grade = grade_value
    db.session.commit()
    flash('Grade updated.', 'success')
    return redirect(url_for('teacher.course', course_id=course_id))
