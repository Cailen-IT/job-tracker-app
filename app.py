from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "dev_secret"

# DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# MODELS
# =========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(50), default="Applied")
    user_email = db.Column(db.String(120), nullable=False)

# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return render_template("index.html")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            return "User already exists"

        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session["user"] = email
            return redirect(url_for("dashboard"))

        return "Invalid credentials"

    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    jobs = Job.query.filter_by(user_email=session["user"]).all()
    return render_template("dashboard.html", jobs=jobs)

# ADD JOB
@app.route("/add-job", methods=["GET", "POST"])
def add_job():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]

        job = Job(
            company=company,
            role=role,
            status="Applied",
            user_email=session["user"]
        )

        db.session.add(job)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("add_job.html")

# DELETE JOB
@app.route("/delete-job/<int:job_id>")
def delete_job(job_id):
    if "user" not in session:
        return redirect(url_for("login"))

    job = Job.query.get(job_id)

    if job and job.user_email == session["user"]:
        db.session.delete(job)
        db.session.commit()

    return redirect(url_for("dashboard"))

# UPDATE STATUS
@app.route("/update-status/<int:job_id>/<status>")
def update_status(job_id, status):
    if "user" not in session:
        return redirect(url_for("login"))

    job = Job.query.get(job_id)

    if job and job.user_email == session["user"]:
        job.status = status
        db.session.commit()

    return redirect(url_for("dashboard"))

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# =========================
# INIT DB
# =========================
with app.app_context():
    db.create_all()

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)