from app import app
from flask import render_template, request, session, url_for, redirect, flash
from models import db, User, Trek, Book


@app.route('/user/dashboard')
def user_dashboard():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))
    if session["role"] != "User":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    Available_trek = Trek.query.filter_by(Status='Open').limit(3).all()
    open_treks_count = Trek.query.filter_by(Status="Open").count()
    book = Book.query.filter_by(User_Id=session['user_id'], Status="Booked").count()
    complete_count = Book.query.filter_by(User_Id=session['user_id'], Status="Completed").count()
    my_bookings_list = Book.query.filter_by(User_Id=session['user_id']).order_by(Book.booking_id.desc()).all()

    return render_template("user/user_dashboard.html", current_user=user, book_count=open_treks_count,
                            complete_count=complete_count, booking_count=book, my_bookings=my_bookings_list,
                            treks=Available_trek)


@app.route('/user/browse')
def browse():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "User":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()
    difficulty = request.args.get("difficulty")
    location = request.args.get("location")

    trek = Trek.query.filter(Trek.Status == "Open")
    if search:
        trek = trek.filter(Trek.Trek_Name.ilike(f"%{search}%"))
    if difficulty:
        trek = trek.filter(Trek.Difficulty == difficulty)
    if location:
        trek = trek.filter(Trek.Location == location)
    trek = trek.order_by(Trek.Trek_Id.desc()).all()
    locations = []
    for loc in db.session.query(Trek.Location).distinct().all():
        locations.append(loc[0])

    return render_template("user/user_booking.html", trek=trek, locations=locations, search=search,
                            difficulty=difficulty)


@app.route("/user/my_bookings")
def my_bookings():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "User":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    book = Book.query.filter_by(User_Id=session["user_id"]) \
        .order_by(Book.Booking_Date.desc()) \
        .all()
    return render_template("user/user_my_bookings.html", book=book)


@app.route("/book/<int:id>", methods=["POST", "GET"])
def booking_trek(id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "User":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    trek = Trek.query.get_or_404(id)

    if trek.Status != "Open":
        flash("booking is closed")
        return redirect(url_for("browse"))
    if trek.Available_Slots <= 0:
        flash("booking is closed")
        return redirect(url_for("browse"))
    already_booked = Book.query.filter_by(User_Id=user_id, Trek_Id=id, Status="Booked").first()
    if already_booked:
        flash("already booked")
        return redirect(url_for("my_bookings"))
    booking = Book(User_Id=user_id, Trek_Id=trek.Trek_Id, Status="Booked")
    trek.Available_Slots -= 1
    if trek.Available_Slots == 0:
        trek.Status = "Closed"
    db.session.add(booking)
    db.session.commit()
    return redirect(url_for("my_bookings"))


@app.route("/user/cancel/<int:booking_id>", methods=["POST", "GET"])
def cancel_booking(booking_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "User":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    book = Book.query.get_or_404(booking_id)
    if book.User_Id != session["user_id"]:
        flash("You can only cancel your own bookings.", "danger")
        return redirect(url_for("my_bookings"))
    if book.Status != "Booked":
        flash("This booking is already cancelled or completed.", "danger")
        return redirect(url_for("my_bookings"))
    book.Status = "Cancelled"
    trek = book.trek
    if trek.Available_Slots < trek.Total_Slots:
        trek.Available_Slots += 1
    if trek.Status == "Closed" and trek.Available_Slots > 0:
        trek.Status = "Open"

    db.session.commit()
    return redirect(url_for("my_bookings"))


@app.route("/user/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "User":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    user = User.query.get(session['user_id'])
    contact = user.Contact
    if request.method == "POST":
        name = request.form.get("name")
        contact = request.form.get("contact")

        user.Username = name
        user.Contact = contact

        db.session.commit()
        return redirect(url_for("profile"))
    return render_template("user/user_profile.html", user=user)
