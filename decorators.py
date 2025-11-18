from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user

from models import Course


def roles_required(*roles):
    """Ensure the logged in user has one of the supplied roles."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("Access denied.", "error")
                return redirect(url_for('auth.login'))
            return func(*args, **kwargs)
        return wrapper
    return decorator


def owns_course_or_admin(course_id):
    """Return True if the current user owns the course or is an admin."""
    if not current_user.is_authenticated:
        return False
    if current_user.role == 'admin':
        return True
    if current_user.role != 'teacher':
        return False
    return bool(Course.query.filter_by(id=course_id, teacher_id=current_user.id).first())
