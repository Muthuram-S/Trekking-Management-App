from app import app
from flask import render_template, request, session, url_for, redirect, flash
from models import db, User, Trek, Book
from datetime import datetime


@app.route('/admin')
def admin():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))
    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    trek_detail = Trek.query.limit(5)
    user_list = User.query.limit(5)
    user_count = User.query.filter_by(Role="User").count()
    staff = User.query.filter_by(Role="Staff").count()
    bookings = Book.query.filter_by(Status="Booked").count()
    trek = Trek.query.count()
    users = User.query.filter_by(Role='User').all()
    for user in users:
        user.bookings_count = Book.query.filter_by(User_Id=user.Id, Status="Booked").count()
    return render_template("admin/admin.html", total_user=user_count, total_staff=staff, total_trek=trek,
                            total_bookings=bookings, trek_detail=trek_detail, user_list=user_list, users=users)


@app.route('/admin/edit_trek/<int:trek_id>', methods=['GET', 'POST'])
@app.route("/admin/add_trek", methods=['GET', 'POST'])
def add_trek(trek_id=None):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))
    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    staffs = User.query.filter_by(Role='Staff', Status="Approved").all()
    trek = Trek.query.filter_by(Trek_Id=trek_id).first()
    if request.method == "POST":
        name = request.form.get('trek_name').strip()
        location = request.form.get('location').strip()
        difficulty = request.form.get('difficulty').strip()
        total_slots = int(request.form.get('total_slots'))
        price = int(request.form.get('price'))
        staff_id = request.form.get("staff_id") or None
        status = request.form.get("status", "Pending")
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        duration = (end_date - start_date).days
        errors = []
        if not name:
            errors.append("Trek name is required")
        if not location:
            errors.append("Location is required")
        if difficulty not in ("Easy", "Moderate", "Hard"):
            errors.append("Please select a valid difficulty")
        if total_slots <= 0:
            errors.append("Total slots must be a positive number.")
        if price < 0:
            errors.append("Price cannot be negative.")
        if end_date < start_date:
            errors.append("Give valid date.")
        if status not in ('Pending', 'Approved', "Open", "Closed", "Completed"):
            errors.append("select proper status")
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template('admin/add_trek.html', staffs=staffs, trek=trek)
        if trek:
            trek.Trek_Name = name
            trek.Location = location
            trek.Difficulty = difficulty
            already_booked = trek.Total_Slots - trek.Available_Slots
            if total_slots < already_booked:
                flash("cannot reduce the total slots below the already booked")
                return redirect(url_for('add_trek', trek_id=trek.Trek_Id))
            trek.Total_Slots = total_slots
            trek.Available_Slots = total_slots - already_booked
            trek.Price = price
            trek.Staff_Id = staff_id
            trek.Description = description
            trek.Start_Date = start_date
            trek.End_Date = end_date
            trek.Duration = duration
            trek.Status = status
            if status == "Completed":
                Book.query.filter_by(Trek_Id=trek.Trek_Id, Status="Booked").update({"Status": "Completed"})
        else:
            new_trek = Trek(Trek_Name=name, Location=location,
                             Difficulty=difficulty, Total_Slots=total_slots,
                             Price=price, Start_Date=start_date, Description=description, Staff_Id=staff_id,
                             End_Date=end_date, Status=status, Available_Slots=total_slots, Duration=duration)
            db.session.add(new_trek)
        db.session.commit()
        flash('Trek added successfully!', 'success')
        return redirect(url_for('trek'))
    return render_template('admin/add_trek.html', staffs=staffs, trek=trek)


@app.route("/admin/user_management", methods=['GET'])
def user_management():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()
    if search == "":
        users = User.query.filter_by(Role="User").all()
    elif search.isdigit():
        users = User.query.filter(User.Role == "User", User.Id == int(search)).all()
    else:
        users = User.query.filter(
            User.Role == "User",
            User.Username.ilike(f"%{search}%")
        ).all()
    for user in users:
        user.bookings_count = Book.query.filter_by(User_Id=user.Id, Status="Booked").count()
    return render_template(
        "admin/admin_user_management.html", users=users, search=search
    )


@app.route("/admin/staff_management", methods=['GET'])
def staff_management():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    search = request.args.get("search", "").strip()
    if search == "":
        staffs = User.query.filter_by(Role="Staff").all()
    elif search.isdigit():
        staffs = User.query.filter(User.Role == "Staff", User.Id == int(search)).all()
    else:
        staffs = User.query.filter(
            User.Role == "Staff",
            User.Username.ilike(f"%{search}%")
        ).all()
    for staff in staffs:
        staff.assigned_treks = Trek.query.filter_by(Staff_Id=staff.Id).all()
    return render_template(
        "admin/admin_staff_management.html",
        staffs=staffs,
        search=search
    )


@app.route("/admin/staffs-blacklist/<int:staff_id>", methods=['GET', 'POST'])
def staff_blacklist(staff_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    staff = User.query.get(staff_id)
    if not staff:
        flash("staff is not found", "danger")
        return redirect(url_for("staff_management"))
    staff.Status = "Blacklisted"
    db.session.commit()
    flash("staff has been blacklisted", "danger")
    return redirect(url_for("staff_management"))


@app.route("/admin/staffs-approve/<int:staff_id>", methods=['GET', 'POST'])
def staff_approve(staff_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    staff = User.query.get(staff_id)
    if not staff:
        flash("staff is not found", "danger")
        return redirect(url_for("staff_management"))
    staff.Status = "Approved"
    db.session.commit()
    flash("staff has been Approved", "success")
    return redirect(url_for("staff_management"))


@app.route("/admin/user-approve/<int:user_id>")
def user_approve(user_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    user = User.query.filter_by(Id=user_id).first()
    user.Status = "Approved"
    db.session.commit()
    flash("User has been Approved", "success")
    return redirect(url_for("user_management"))


@app.route("/admin/user-blacklist/<int:user_id>")
def user_blacklist(user_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    user = User.query.filter_by(Id=user_id).first()
    user.Status = "Blacklisted"
    db.session.commit()
    flash("User has been blacklisted", "danger")
    return redirect(url_for("user_management"))


@app.route("/admin/trek")
def trek():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    search = request.args.get("search", "").strip()
    trek = Trek.query
    if search:
        if search.isdigit():
            trek = trek.filter(Trek.Trek_Id == int(search))
        else:
            trek = trek.filter(Trek.Trek_Name.ilike(f"%{search}%"))
    trek = trek.order_by(Trek.Trek_Id.desc()).all()

    return render_template("admin/admin_trek.html", trek=trek)


@app.route("/admin/bookings")
def bookings():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    book = Book.query.all()
    return render_template("admin/admin_booking.html", book=book)


@app.route("/admin/delete/<int:trek_id>", methods=["POST"])
def delete(trek_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    if Book.query.filter_by(Trek_Id=trek_id, Status="Booked").first():
        flash("Cannot delete trek with active bookings.")
        return redirect(url_for("trek"))
    delete_trek = Trek.query.get_or_404(trek_id)
    db.session.delete(delete_trek)
    db.session.commit()

    return redirect(url_for("trek"))
