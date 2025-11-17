from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint, func
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'devkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, pw): self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=30)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher = db.relationship('User', foreign_keys=[teacher_id])

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.String(5))
    student = db.relationship('User', foreign_keys=[student_id])
    course = db.relationship('Course', foreign_keys=[course_id])
    __table_args__ = (UniqueConstraint('student_id', 'course_id', name='uq_student_course'),)

@login_manager.user_loader
def load_user(uid): return User.query.get(int(uid))

def roles_required(*roles):
    def deco(fn):
        @wraps(fn)
        def inner(*a, **k):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("Access denied.", "error")
                return redirect(url_for('login'))
            return fn(*a, **k)
        return inner
    return deco

def owns_course_or_admin(course_id):
    if current_user.role == 'admin': return True
    if current_user.role != 'teacher': return False
    return bool(Course.query.filter_by(id=course_id, teacher_id=current_user.id).first())

@app.route('/')
def home(): return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username','').strip()
        p = request.form.get('password','')
        user = User.query.filter_by(username=u).first()
        if user and user.check_password(p):
            login_user(user)
            flash('Welcome back!', 'success')
            if user.role == 'student': return redirect(url_for('student_my_classes'))
            if user.role == 'teacher': return redirect(url_for('teacher_dashboard'))
            return redirect('/admin')
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user(); flash('Logged out.','info'); return redirect(url_for('home'))

@app.route('/student/my-classes')
@login_required
@roles_required('student')
def student_my_classes():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    return render_template('student_my_classes.html', enrollments=enrollments)

@app.route('/student/all-classes')
@login_required
def student_all_classes():
    courses = Course.query.order_by(Course.code).all()
    counts = dict(db.session.query(Enrollment.course_id, func.count(Enrollment.id)).group_by(Enrollment.course_id).all())
    return render_template('student_all_classes.html', courses=courses, counts=counts)

@app.route('/student/enroll/<int:course_id>', methods=['POST'])
@login_required
@roles_required('student')
def student_enroll(course_id):
    course = Course.query.get_or_404(course_id)
    exists = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if exists: flash('Already enrolled.','warning'); return redirect(url_for('student_all_classes'))
    count = Enrollment.query.filter_by(course_id=course_id).count()
    if count >= course.capacity: flash('Class is full.','error'); return redirect(url_for('student_all_classes'))
    db.session.add(Enrollment(student_id=current_user.id, course_id=course_id)); db.session.commit()
    flash('Enrolled successfully!','success'); return redirect(url_for('student_my_classes'))

@app.route('/teacher')
@login_required
@roles_required('teacher')
def teacher_dashboard():
    courses = Course.query.filter_by(teacher_id=current_user.id).order_by(Course.code).all()
    return render_template('teacher_dashboard.html', courses=courses)

@app.route('/teacher/course/<int:course_id>')
@login_required
@roles_required('teacher','admin')
def teacher_course(course_id):
    if not owns_course_or_admin(course_id): abort(403)
    course = Course.query.get_or_404(course_id)
    roster = Enrollment.query.filter_by(course_id=course_id).all()
    return render_template('teacher_course.html', course=course, roster=roster)

@app.route('/teacher/course/<int:course_id>/grade', methods=['POST'])
@login_required
@roles_required('teacher','admin')
def teacher_grade(course_id):
    if not owns_course_or_admin(course_id): abort(403)
    student_id = int(request.form['student_id'])
    grade = request.form.get('grade','').strip() or None
    enr = Enrollment.query.filter_by(course_id=course_id, student_id=student_id).first_or_404()
    enr.grade = grade; db.session.commit(); flash('Grade updated.','success')
    return redirect(url_for('teacher_course', course_id=course_id))

class AdminOnlyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    def inaccessible_callback(self, name, **kwargs):
        flash('Admin access required.','error'); return redirect(url_for('login'))

admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin.add_view(AdminOnlyModelView(User, db.session))
admin.add_view(AdminOnlyModelView(Course, db.session))
admin.add_view(AdminOnlyModelView(Enrollment, db.session))

@app.errorhandler(403)
def forbidden(e): return render_template('403.html'), 403
@app.errorhandler(404)
def notfound(e): return render_template('404.html'), 404

def seed():
    db.create_all()
    if not User.query.first():
        admin = User(username='admin', role='admin'); admin.set_password('admin')
        t1 = User(username='turing', role='teacher'); t1.set_password('teacher')
        t2 = User(username='hopper', role='teacher'); t2.set_password('teacher')
        s1 = User(username='alice', role='student'); s1.set_password('student')
        s2 = User(username='bob', role='student'); s2.set_password('student')
        s3 = User(username='charlie', role='student'); s3.set_password('student')
        db.session.add_all([admin, t1, t2, s1, s2, s3]); db.session.flush()
        c1 = Course(code='CS101', title='Intro to CS', capacity=2, teacher_id=t1.id)
        c2 = Course(code='CS201', title='Data Structures', capacity=3, teacher_id=t1.id)
        c3 = Course(code='MTH100', title='Calculus I', capacity=2, teacher_id=t2.id)
        db.session.add_all([c1, c2, c3]); db.session.commit()

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True)
