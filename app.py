from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

USERS_FILE = "users.json"

@app.after_request
def add_no_cache(response):
    if "username" in session:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        users = load_users()
        if username in users and users[username]["password"] == hash_password(password):
            session["username"] = username
            session["fullname"] = users[username]["fullname"]
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "username" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        fullname         = request.form.get("fullname", "").strip()
        username         = request.form.get("username", "").strip()
        email            = request.form.get("email", "").strip()
        password         = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([fullname, username, email, password]):
            flash("All fields are required.", "error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        else:
            users = load_users()
            if username in users:
                flash("Username already taken. Choose another.", "error")
            else:
                users[username] = {
                    "fullname": fullname,
                    "email": email,
                    "password": hash_password(password),
                    "created_at": datetime.now().isoformat()
                }
                save_users(users)
                flash("Account created! Please sign in.", "success")
                return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        flash("Please log in to continue.", "error")
        return redirect(url_for("login"))

    fullname = session.get("fullname", session["username"])
    initial  = fullname[0].upper()
    date     = datetime.now().strftime("%A, %B %d, %Y")

    return render_template("dashboard.html", fullname=fullname, initial=initial, date=date)


@app.route("/logout")
def logout():
    session.clear()
    flash("You've been signed out.", "success")
    response = redirect(url_for("login"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    print("\n  ⬡  Vault is running → http://127.0.0.1:5000\n")
    app.run(debug=True)