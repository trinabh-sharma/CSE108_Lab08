from functools import wraps

from flask import redirect, url_for, flash
from flask_login import current_user

from models import Course


def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in first.", "error")
                return redirect(url_for("auth.login"))
            if current_user.role not in roles:
                flash("Access denied.", "error")
                return redirect(url_for("home"))
            return fn(*args, **kwargs)

        return inner

    return wrapper


def owns_course_or_admin(course_id: int) -> bool:
    if not current_user.is_authenticated:
        return False
    if current_user.role == "admin":
        return True
    if current_user.role != "teacher":
        return False
    return Course.query.filter_by(id=course_id, teacher_id=current_user.id).first() is not None
