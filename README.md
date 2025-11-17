# Lab 8 — Student Enrollment Web App
Login, student views (my classes, all classes, enroll with capacity + counts), teacher roster + grading, and admin CRUD.

## Run
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed.py
export FLASK_APP=app.py          # Windows: $env:FLASK_APP='app.py'
flask run
