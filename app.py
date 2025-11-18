from flask import Flask, render_template

from admin_panel import init_admin
from auth_routes import auth_bp
from extensions import db, login_manager
from models import seed as seed_data
from student_routes import student_bp
from teacher_routes import teacher_bp


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'devkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    init_admin(app)

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def notfound(error):
        return render_template('404.html'), 404

    return app


app = create_app()
seed = seed_data


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
