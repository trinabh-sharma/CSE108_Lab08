from extensions import db
from app import app
from models import User, Course


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(username="admin", role="admin")
        admin.set_password("admin")

        t1 = User(username="turing", role="teacher")
        t1.set_password("teacher")

        t2 = User(username="hopper", role="teacher")
        t2.set_password("teacher")

        s1 = User(username="alice", role="student")
        s1.set_password("student")

        s2 = User(username="bob", role="student")
        s2.set_password("student")

        s3 = User(username="charlie", role="student")
        s3.set_password("student")

        db.session.add_all([admin, t1, t2, s1, s2, s3])
        db.session.flush()

        c1 = Course(code="CS101", title="Intro to CS", capacity=2, teacher_id=t1.id)
        c2 = Course(code="CS201", title="Data Structures", capacity=3, teacher_id=t1.id)
        c3 = Course(code="MTH100", title="Calculus I", capacity=2, teacher_id=t2.id)

        db.session.add_all([c1, c2, c3])
        db.session.commit()

        print("Seed complete.")
        print("Admin: admin / admin")
        print("Teachers: turing / teacher, hopper / teacher")
        print("Students: alice, bob, charlie / student")


if __name__ == "__main__":
    seed()
