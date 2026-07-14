from app import app
from flask import render_template, request, session, url_for, redirect, flash
from models import db, User, Trek, Book


@app.route("/staff/dashboard")
def staff_dashboard():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Staff":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    user_name = User.query.filter_by(Id=session['user_id']).first().Username
    staff_id = session["user_id"]
    treks_count = Trek.query.filter_by(Staff_Id=staff_id).all()

    count_trek = Book.query.join(Trek).filter(Book.Status == "Booked", Trek.Staff_Id == session["user_id"]).count()
    trek = Trek.query.filter_by(Staff_Id=staff_id).all()
    return render_template("staff/staff_dashboard.html", trek=trek, user_name=user_name, count_trek=count_trek,
                            treks_count=len(treks_count))


@app.route("/staff/update_trek/<int:trek_id>", methods=['GET', 'POST'])
def update_trek(trek_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Staff":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    trek = Trek.query.get_or_404(trek_id)

    if trek.Staff_Id != session["user_id"]:
        flash("You are not assigned to this trek.", "danger")
        return redirect(url_for("staff_dashboard"))

    if request.method == "POST":
        slots = int(request.form.get("available_slots"))
        status = request.form.get("status")
        if slots < 0:
            flash("Slots cannot be negative.", "danger")
            return redirect(url_for("update_trek", trek_id=trek_id))
        if slots > trek.Total_Slots:
            flash("Available slots cannot exceed total slots.", "danger")
            return redirect(url_for("update_trek", trek_id=trek_id))
        if status not in ["Open", "Closed", "Completed"]:
            flash("Invalid status.", "danger")
            return redirect(url_for("update_trek", trek_id=trek_id))
        trek.Available_Slots = slots
        trek.Status = status
        if status == "Completed":
            Book.query.filter_by(Trek_Id=trek.Trek_Id, Status="Booked").update({"Status": "Completed"})
        db.session.commit()
        return redirect(url_for("my_trek"))
    return render_template("staff/staff_update.html", trek=trek)


@app.route("/staff/participants/<int:trek_id>")
def participants(trek_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Staff":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    trek = Trek.query.get_or_404(trek_id)
    if trek.Staff_Id != session["user_id"]:
        flash("You are not assigned to this trek.", "danger")
        return redirect(url_for("my_trek"))
    book = Book.query.filter_by(Trek_Id=trek_id, Status="Booked").all()
    return render_template("staff/staff_participants.html", trek=trek, book=book)


@app.route("/staff/my_trek")
def my_trek():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Staff":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    trek = Trek.query.filter_by(Staff_Id=session["user_id"]).all()
    return render_template("staff/staff_my_trek.html", trek=trek)


@app.route("/staff/profile", methods=["GET", "POST"])
def staff_profile():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Staff":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    staff = User.query.get(session['user_id'])
    contact = staff.Contact
    if request.method == "POST":
        name = request.form.get("name")
        contact = request.form.get("contact")
        if not name:
            flash('Name is required', 'danger')
            return redirect(url_for('staff_profile'))
        staff.Username = name
        staff.Contact = contact
        db.session.commit()
        return redirect(url_for("staff_profile"))
    return render_template("staff/staff_profile.html", user=staff)
