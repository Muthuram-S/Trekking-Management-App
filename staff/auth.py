from app import app
from flask import render_template, request, session, url_for, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(Email=email).first()

        if user and check_password_hash(user.Password, password):
            if user.Status == "Blacklisted":
                session.clear()
                return redirect(url_for("login"))
            session["user_id"] = user.Id
            session["role"] = user.Role

        else:
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        if user.Role == "Admin":
            return redirect(url_for("admin"))
        if user.Role == "Staff":
            if user.Status == "Approved":
                return redirect(url_for("staff_dashboard"))
            if user.Status == "Pending":
                flash("Your account is waiting for admin approval.", "warning")
                return redirect(url_for('login'))

        if user.Role == "User":
            return redirect(url_for("user_dashboard"))

    return render_template('login.html')


@app.route("/", methods=['GET', 'POST'])
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('mail')
        password = request.form.get('password')
        contact = request.form.get('contact')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        if role not in ("Staff", "User"):
            role = "User"
        exist_user = User.query.filter_by(Email=email).first()

        error_reg = []

        if not name:
            error_reg.append("Name is required")
        if "@" not in email:
            error_reg.append("Invalid email")
        if len(password) < 6:
            error_reg.append("Password must be at least 6 character long")
        if password != confirm_password:
            error_reg.append("password do not match")

        if exist_user:
            error_reg.append("This email already exists")
        if error_reg:
            for e in error_reg:
                flash(e, "danger")
            return render_template("register.html", form=request.form)
        if role == 'Staff':
            status = 'Pending'
        else:
            status = 'Approved'

        hash_password = generate_password_hash(password)

        new_user = User(Username=name, Email=email, Password=hash_password, Role=role, Status=status, Contact=contact)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    session.pop("user_id", None)
    session.pop("role", None)
    return redirect(url_for('login'))
