from flask import redirect, url_for, flash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms import Form
from wtforms.meta import DefaultMeta

from extensions import db
from models import User, Course, Enrollment


class AdminCompatibleForm(Form):
    """WTForms 3 compatibility wrapper for Flask-Admin."""

    class Meta(DefaultMeta):
        def bind_field(self, form, unbound_field, options):
            flags = options.get('flags')
            if isinstance(flags, (tuple, list, set)):
                options['flags'] = {flag: True for flag in flags}
            return super().bind_field(form, unbound_field, options)


class AdminOnlyModelView(ModelView):
    form_base_class = AdminCompatibleForm

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        flash('Admin access required.', 'error')
        return redirect(url_for('auth.login'))


class UserModelView(AdminOnlyModelView):
    column_list = ['id', 'username', 'role']
    column_searchable_list = ['username', 'role']
    column_filters = ['role']
    form_columns = ['username', 'password_hash', 'role']
    can_create = True
    can_edit = True
    can_delete = True


class CourseModelView(AdminOnlyModelView):
    column_list = ['id', 'code', 'title', 'capacity', 'teacher']
    column_searchable_list = ['code', 'title']
    column_filters = ['teacher_id']
    form_columns = ['code', 'title', 'capacity', 'teacher']
    can_create = True
    can_edit = True
    can_delete = True


class EnrollmentModelView(AdminOnlyModelView):
    column_list = ['id', 'student', 'course', 'grade']
    column_searchable_list = ['grade']
    column_filters = ['student_id', 'course_id']
    form_columns = ['student', 'course', 'grade']
    can_create = True
    can_edit = True
    can_delete = True


def init_admin(app):
    admin = Admin(
        app, 
        name='Admin Panel', 
        template_mode='bootstrap3', 
        url='/admin',
        base_template='admin/custom_base.html'
    )
    admin.add_view(UserModelView(User, db.session, name='Users', endpoint='admin_users'))
    admin.add_view(CourseModelView(Course, db.session, name='Courses', endpoint='admin_courses'))
    admin.add_view(EnrollmentModelView(Enrollment, db.session, name='Enrollments', endpoint='admin_enrollments'))
    return admin
