"""
Session-based auth + profile routes using the same MySQL database as scan history (blocksentinel.users).
Registers routes on the main Flask app.
"""
from __future__ import annotations

import os
import uuid
from functools import wraps

import db_common
import pymysql
from pymysql import err as pymysql_err
from pymysql.cursors import DictCursor
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

_pymysql_auth_conn: pymysql.Connection | None = None


def _auth_connect() -> pymysql.Connection:
    global _pymysql_auth_conn
    p = db_common.mysql_params()
    if _pymysql_auth_conn is None:
        _pymysql_auth_conn = pymysql.connect(
            host=p["host"],
            port=p["port"],
            user=p["user"],
            password=p["password"],
            database=p["database"],
            charset=p["charset"],
            cursorclass=DictCursor,
            autocommit=False,
        )
    try:
        _pymysql_auth_conn.ping(reconnect=True)
    except Exception:
        _pymysql_auth_conn.close()
        _pymysql_auth_conn = pymysql.connect(
            host=p["host"],
            port=p["port"],
            user=p["user"],
            password=p["password"],
            database=p["database"],
            charset=p["charset"],
            cursorclass=DictCursor,
            autocommit=False,
        )
    return _pymysql_auth_conn


def get_auth_cursor():
    return _auth_connect().cursor()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("loginpage"))
        return f(*args, **kwargs)

    return decorated


def _commit():
    _auth_connect().commit()


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _mysql_access_message(exc: Exception) -> str | None:
    if isinstance(exc, pymysql_err.OperationalError) and exc.args and exc.args[0] == 1045:
        return (
            "MySQL access denied (often: password not loaded). Put MYSQL_PASSWORD in the .env file "
            "next to main.py, or use legacy PASSWORD=… there, then restart Flask from any folder."
        )
    return None


def get_user_data(username: str):
    cur = get_auth_cursor()
    cur.execute(
        "SELECT FirstName, LastName, mobile_number, bio, country, username, profile_pic "
        "FROM users WHERE username=%s",
        (username,),
    )
    return cur.fetchone()


def register_auth_routes(app: Flask) -> None:
    upload_root = os.path.join(app.static_folder or "", "uploads", "avatars")
    os.makedirs(upload_root, exist_ok=True)
    app.config.setdefault("UPLOAD_FOLDER", upload_root)
    app.config.setdefault("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)

    @app.route("/")
    def home():
        user = None
        if "user" in session:
            user = get_user_data(session["user"])
            if user and user.get("profile_pic") and not str(user["profile_pic"]).startswith("/"):
                user["profile_pic"] = "/" + str(user["profile_pic"])
        return render_template("index.html", user=user)

    @app.route("/loginpage")
    def loginpage():
        return render_template("login.html")

    @app.route("/login")
    def login_get_redirect():
        """Avoid 404 when users open /login in the browser (form still POSTs to /login)."""
        return redirect(url_for("loginpage"))

    @app.route("/profile")
    @login_required
    def profile():
        user = get_user_data(session["user"])
        if not user:
            return redirect(url_for("loginpage"))
        if user.get("profile_pic") and not str(user["profile_pic"]).startswith("/"):
            user["profile_pic"] = "/" + str(user["profile_pic"])
        return render_template("profile.html", user=user)

    @app.route("/dashboard")
    @login_required
    def dashboard_page():
        user = get_user_data(session["user"])
        if user and user.get("profile_pic") and not str(user["profile_pic"]).startswith("/"):
            user["profile_pic"] = "/" + str(user["profile_pic"])
        return render_template("dashboard.html", user=user)

    @app.route("/login", methods=["POST"])
    def login():
        user = request.form.get("email")
        password = request.form.get("password")
        try:
            cur = get_auth_cursor()
            cur.execute("SELECT password FROM users WHERE username=%s", (user,))
            myresult = cur.fetchone()
        except pymysql_err.OperationalError as e:
            msg = _mysql_access_message(e)
            if msg:
                flash(msg, "error")
                return redirect(url_for("loginpage"))
            raise
        if myresult:
            if check_password_hash(myresult["password"], password):
                session.permanent = True
                session["user"] = user
                return redirect(url_for("dashboard_page"))
            flash("Incorrect password. Try again or reset your password.", "error")
            return redirect(url_for("loginpage"))
        flash("No account found for that email. Check the address or sign up.", "error")
        return redirect(url_for("loginpage"))

    @app.route("/logout")
    def logout():
        session.pop("user", None)
        return redirect(url_for("loginpage"))

    @app.route("/register", methods=["POST"])
    def register():
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("loginpage", tab="signup"))

        try:
            cur = get_auth_cursor()
            cur.execute("SELECT * FROM users WHERE username=%s", (email,))
            if cur.fetchone():
                flash("An account with this email already exists. Try logging in.", "error")
                return redirect(url_for("loginpage", tab="signup"))

            hashed_password = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (FirstName, LastName, username, password) VALUES (%s, %s, %s, %s)",
                (first_name, last_name, email, hashed_password),
            )
            _commit()
        except pymysql_err.OperationalError as e:
            msg = _mysql_access_message(e)
            if msg:
                flash(msg, "error")
                return redirect(url_for("loginpage", tab="signup"))
            raise

        session.permanent = True
        session["user"] = email
        return redirect(url_for("profile"))

    @app.route("/profile/update", methods=["POST"])
    @login_required
    def profile_update():
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "error": "Invalid request body"}), 400

        first_name = (data.get("FirstName") or "").strip()
        last_name = (data.get("LastName") or "").strip()
        mobile_number = (data.get("mobile_number") or "").strip()
        bio = (data.get("bio") or "").strip()
        country = (data.get("country") or "").strip()

        if not first_name:
            return jsonify({"success": False, "error": "First name is required"}), 400
        if not last_name:
            return jsonify({"success": False, "error": "Last name is required"}), 400

        cur = get_auth_cursor()
        cur.execute(
            "UPDATE users SET FirstName=%s, LastName=%s, mobile_number=%s, bio=%s, country=%s WHERE username=%s",
            (first_name, last_name, mobile_number or None, bio or None, country or None, session["user"]),
        )
        _commit()
        return jsonify({"success": True})

    @app.route("/profile/change-password", methods=["POST"])
    @login_required
    def change_password():
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "error": "Invalid request body"}), 400

        current_password = data.get("current_password", "")
        new_password = data.get("new_password", "")

        if not current_password or not new_password:
            return jsonify({"success": False, "error": "All fields are required"}), 400
        if len(new_password) < 8:
            return jsonify({"success": False, "error": "Password must be at least 8 characters"}), 400

        cur = get_auth_cursor()
        cur.execute("SELECT password FROM users WHERE username=%s", (session["user"],))
        row = cur.fetchone()
        if not row or not check_password_hash(row["password"], current_password):
            return jsonify({"success": False, "error": "Current password is incorrect"}), 400

        hashed = generate_password_hash(new_password)
        cur.execute("UPDATE users SET password=%s WHERE username=%s", (hashed, session["user"]))
        _commit()
        return jsonify({"success": True})

    @app.route("/profile/upload-avatar", methods=["POST"])
    @login_required
    def upload_avatar():
        if "profile_pic" not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400

        file = request.files["profile_pic"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400
        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "File type not allowed. Use PNG, JPG, GIF, or WEBP"}), 400

        ext = file.filename.rsplit(".", 1)[1].lower()
        raw_name = f"{session['user'].replace('@','_').replace('.','_')}_{uuid.uuid4().hex[:8]}.{ext}"
        filename = secure_filename(raw_name)

        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        cur = get_auth_cursor()
        cur.execute("SELECT profile_pic FROM users WHERE username=%s", (session["user"],))
        row = cur.fetchone()

        def _fs_from_url(u: str | None) -> str | None:
            if not u:
                return None
            u = str(u).lstrip("/").replace("\\", "/")
            if u.startswith("static/"):
                return os.path.join(app.static_folder, u[len("static/") :])
            if u.startswith("uploads/avatars/"):
                return os.path.join(app.static_folder, u)
            return None

        if row and row.get("profile_pic"):
            old_fs = _fs_from_url(row["profile_pic"]) or _fs_from_url("static/" + row["profile_pic"].lstrip("/"))
            if old_fs and os.path.isfile(old_fs) and os.path.abspath(old_fs) != os.path.abspath(save_path):
                try:
                    os.remove(old_fs)
                except OSError:
                    pass

        url_path = "/static/uploads/avatars/" + filename
        cur.execute("UPDATE users SET profile_pic=%s WHERE username=%s", (url_path, session["user"]))
        _commit()

        return jsonify({"success": True, "url": url_path})
