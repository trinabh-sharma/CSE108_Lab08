from flask import redirect, url_for, flash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from extensions import db
from models import User, Course, Enrollment


class AdminOnlyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == "admin"

    def inaccessible_callback(self, name, **kwargs):
        flash("Admin access required.", "error")
        return redirect(url_for("auth.login"))


def init_admin(app):
    admin = Admin(app, name="Admin Panel", template_mode="bootstrap3")
    admin.add_view(AdminOnlyModelView(User, db.session))
    admin.add_view(AdminOnlyModelView(Course, db.session))
    admin.add_view(AdminOnlyModelView(Enrollment, db.session))
    return admin
