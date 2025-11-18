from flask import Flask, render_template, redirect, url_for
from flask_login import current_user

from extensions import db, login_manager
from models import User
from auth_routes import auth_bp
from student_routes import student_bp
from teacher_routes import teacher_bp
from admin_panel import init_admin


app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-key"  # change in real use
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///school.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(teacher_bp)
init_admin(app)


@app.route("/")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    return render_template("index.html")


@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
