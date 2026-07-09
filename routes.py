
from app import app
from flask import render_template,request,session,url_for,redirect,flash
from werkzeug.security import check_password_hash,generate_password_hash
from models import db,User,Trek,Book
from datetime import date


@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')
        
        user=User.query.filter_by(Email=email).first()

        if user and check_password_hash(user.Password,password):
            if user.Status=="Blacklisted":
                session.clear()
                return redirect(url_for("login"))
            session["user_id"]=user.Id
            session["role"]=user.Role
          
        else:
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        if user.Role =="Admin":
            return redirect(url_for("admin"))
        if user.Role =="Staff":
            if user.Status=="Approved":
                return redirect(url_for("staff_dashboard"))
            if user.Status =="Pending":
                flash("Your account is waiting for admin approval.", "warning")
                return redirect(url_for('login'))

        if user.Role =="User":
            return redirect(url_for("user_dashboard"))
    
    return render_template('login.html')


@app.route("/",methods=['GET','POST'])  
@app.route("/register",methods=['GET','POST'])
def register():
    if request.method =='POST':
        name=request.form.get('name')
        email=request.form.get('mail')
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')
        role=request.form.get('role')
        if role not in ("Staff", "User"):
            role = "User"
        exist_user=User.query.filter_by(Email=email).first()

        error_reg=[]

        if not name:
            error_reg.append("Name is required")
        if "@" not in email:
            error_reg.append("Invalid email")
        if len(password)<6:
            error_reg.append("Password must be at least 6 character long")
        if password!=confirm_password:
            error_reg.append("password do not match")
  
        if exist_user:
            error_reg.append("This email already exists")
        if error_reg:
            for e in error_reg:
                flash(e, "danger")
            return render_template("register.html", form=request.form)
        if role=='Staff':
            status='Pending'
        else:
            status='Approved'
      

        hash_password=generate_password_hash(password)
        

        new_user=User(Username=name,Email=email,Password=hash_password,Role=role,Status=status)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    session.pop("user_id", None)
    session.pop("role", None) 
    return redirect (url_for('login'))

@app.route('/admin')
def admin():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))
    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    trek_detail=Trek.query.limit(5)
    user_list=User.query.limit(5)
    user_count=User.query.filter_by(Role="User").count()
    staff=User.query.filter_by(Role="Staff").count()
    bookings=Book.query.filter_by(Status="Booked").count()
    trek=Trek.query.count()
    users=User.query.filter_by(Role='User').all()
    for user in users:
        user.bookings_count=Book.query.filter_by(User_Id=user.Id,Status="Booked").count()
    return render_template("admin.html",count_user=user_count,count_staff=staff,trek=trek,total_bookings=bookings,trek_detail=trek_detail,user_list=user_list,users=users)


@app.route('/admin/edit_trek/<int:trek_id>',methods=['GET','POST'])
@app.route("/admin/add_trek",methods=['GET','POST']) 
def add_trek(trek_id=None):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))
    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    from datetime import datetime
    staffs=User.query.filter_by(Role='Staff',Status="Approved").all()
    trek=Trek.query.filter_by(Trek_Id=trek_id).first()
    if request.method=="POST":
        name =request.form.get('trek_name').strip()
        location=request.form.get('location').strip()
        difficulty=request.form.get('difficulty').strip()
        total_slots=int(request.form.get('total_slots'))
        price=int(request.form.get('price'))
        staff_id=request.form.get("staff_id") or None
        status = request.form.get("status","Pending")
        description=request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        duration=(end_date-start_date).days
        errors=[]
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
        if status not in ('Pending','Approved',"Open","Closed","Completed"):
            errors.append("select proper status")
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template('add_trek.html', staffs=staffs, trek=trek)
        if trek:
            trek.Trek_Name = name
            trek.Location = location
            trek.Difficulty = difficulty
            already_booked = trek.Total_Slots - trek.Available_Slots
            if total_slots<already_booked:
                flash("cannot reduce the total slots below the already booked")
                return redirect(url_for('add_trek',trek_id=trek.Trek_Id))
            trek.Total_Slots = total_slots
            trek.Available_Slots=total_slots-already_booked
            trek.Price = price
            trek.Staff_Id = staff_id
            trek.Description = description
            trek.Start_Date = start_date
            trek.End_Date = end_date
            trek.Duration=duration
            trek.Status = status
            if status=="Completed":
                Book.query.filter_by(Trek_Id=trek.Trek_Id, Status="Booked").update({"Status":"Completed"})
        else:
            new_trek=Trek(Trek_Name=name,Location=location,
            Difficulty=difficulty,Total_Slots=total_slots,
            Price=price,Start_Date=start_date,Description=description,Staff_Id = staff_id,
            End_Date=end_date,Status=status,Available_Slots=total_slots,Duration=duration)
            db.session.add(new_trek)
        db.session.commit()
        flash('Trek added successfully!', 'success')
        return redirect(url_for('trek'))
    return render_template('add_trek.html',staffs=staffs,trek=trek)




@app.route("/admin/user_management")
def user_management():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    
    search = request.args.get("search", "").strip()
    if search=="":
        users = User.query.filter_by(Role="User").all()
    elif search.isdigit():
        users = User.query.filter(User.Role == "User", User.Id == int(search)).all()

    else:
        users=User.query.filter(
            User.Role=="User",
            User.Username.ilike(f"%{search}%")
        ).all()
    for user in users:
        user.bookings_count=Book.query.filter_by(User_Id=user.Id,Status="Booked").count()
    return render_template(
        "admin_user_management.html",users=users,search=search
    )

@app.route("/admin/staff_management",methods=['GET'])

def staff_management():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    search = request.args.get("search", "").strip()
    if search=="":
        staffs = User.query.filter_by(Role="Staff").all()
    elif search.isdigit():
        staffs = User.query.filter(User.Role == "Staff", User.Id == int(search)).all()
    else:
        staffs=User.query.filter(
            User.Role=="Staff",
            User.Username.ilike(f"%{search}%")
        ).all()
    for staff in staffs:
        staff.assigned_treks = Trek.query.filter_by(Staff_Id=staff.Id).all()
    return render_template(
        "admin_staff_management.html",
        staffs=staffs,
        search=search
    )

@app.route("/admin/staffs-blacklist/<int:staff_id>",methods=['GET','POST'])
def staff_blacklist(staff_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    staff=User.query.get(staff_id)
    if not staff:
        flash("staff is not found","danger")
        return redirect(url_for("staff_management"))
    staff.Status="Blacklisted"
    db.session.commit()
    flash("staff has been blacklisted","danger")
    return redirect(url_for("staff_management"))
@app.route("/admin/staffs-approve/<int:staff_id>",methods=['GET','POST'])
def staff_approve(staff_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    staff=User.query.get(staff_id)
    if not staff:
        flash("staff is not found","danger")
        return redirect(url_for("staff_management"))
    staff.Status="Approved"
    db.session.commit()
    flash("staff has been Approved","success")
    return redirect(url_for("staff_management"))

@app.route("/admin/user-approve/<int:user_id>")
def user_approve(user_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    user=User.query.filter_by(Id=user_id).first()
    user.Status="Approved"
    db.session.commit()
    flash("User has been Approved","success")
    return redirect(url_for("user_management"))

@app.route("/admin/user-blacklist/<int:user_id>")
def user_blacklist(user_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    user=User.query.filter_by(Id=user_id).first()
    user.Status="Blacklisted"
    db.session.commit()
    flash("User has been blacklisted","danger")
    return redirect(url_for("user_management"))

@app.route("/admin/trek")
def trek():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    search=request.args.get("search","").strip()
    trek=Trek.query
    if search:
        if search.isdigit():
            trek=trek.filter(Trek.Trek_Id==int(search))
        else:
            trek=trek.filter(Trek.Trek_Name.ilike(f"%{search}%"))
    trek = trek.order_by(Trek.Trek_Id.desc()).all()
    
    return render_template("admin_trek.html",trek=trek)

@app.route("/admin/bookings")
def bookings():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    book=Book.query.all()
    return render_template("admin_booking.html",book=book)

@app.route("/admin/delete/<int:trek_id>", methods=["POST"])
def delete(trek_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    if Book.query.filter_by(Trek_Id=trek_id,Status="Booked").first():
        flash("Cannot delete trek with active bookings.")
        return redirect(url_for("trek"))
    delete_trek = Trek.query.get_or_404(trek_id)
    db.session.delete(delete_trek)
    db.session.commit()
    
    return redirect(url_for("trek"))


@app.route("/staff/dashboard")
def staff_dashboard():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Staff":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    user_name=User.query.filter_by(Id=session['user_id']).first().Username
    staff_id=session["user_id"]
    treks_count = Trek.query.filter_by(Staff_Id=staff_id).all()
    
    count_trek=Book.query.join(Trek).filter(Book.Status == "Booked",Trek.Staff_Id == session["user_id"]).count()
    trek=Trek.query.filter_by(Staff_Id=staff_id).all()
    return render_template("staff_dashboard.html", trek=trek,user_name=user_name,count_trek=count_trek,treks_count=len(treks_count))
@app.route("/staff/update_trek/<int:trek_id>",methods=['GET','POST'])
def update_trek(trek_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Staff":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    
    trek = Trek.query.get_or_404(trek_id)

    if trek.Staff_Id != session["user_id"]:
        flash("You are not assigned to this trek.","danger")
        return redirect(url_for("staff_dashboard"))
    
    if request.method == "POST":
        slots=int(request.form.get("available_slots"))
        status = request.form.get("status")
        if slots<0 :
            flash("Slots cannot be negative.", "danger")
            return redirect(url_for("update_trek", trek_id=trek_id))
        if slots > trek.Total_Slots:
            flash("Available slots cannot exceed total slots.", "danger")
            return redirect(url_for("update_trek", trek_id=trek_id))
        if status not in ["Open", "Closed","Completed"]:
            flash("Invalid status.", "danger")
            return redirect(url_for("update_trek", trek_id=trek_id))
        trek.Available_Slots=slots  
        trek.Status=status
        if status=="Completed":
                Book.query.filter_by(Trek_Id=trek.Trek_Id, Status="Booked").update({"Status":"Completed"})
        db.session.commit()
        return redirect(url_for("my_trek"))
    return render_template("staff_update.html", trek=trek)

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
    book=Book.query.filter_by(Trek_Id=trek_id,Status="Booked").all()
    return render_template("staff_participants.html",trek=trek,book=book)


@app.route("/staff/my_trek")
def my_trek():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Staff":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    trek = Trek.query.filter_by(Staff_Id=session["user_id"]).all()
    return render_template("staff_my_trek.html", trek=trek)


@app.route("/staff/profile",methods=["GET","POST"])
def staff_profile():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "Staff":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    staff=User.query.get(session['user_id'])
    if request.method=="POST":
        name=request.form.get("name")
        if not name:
            flash('Name is required','danger')
            return redirect(url_for('staff_profile'))
        staff.Username=name
        db.session.commit()
        return redirect(url_for("staff_profile"))
    return render_template("staff_profile.html",user=staff)

@app.route('/user/dashboard')
def user_dashboard():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))
    if session["role"] != "User":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    user=User.query.get(session["user_id"])
    Available_trek = Trek.query.filter_by(Status='Open').limit(3).all()
    open_treks_count = Trek.query.filter_by(Status="Open").count()
    book=Book.query.filter_by(User_Id=session['user_id'],Status="Booked").count()
    complete_count=Book.query.filter_by(User_Id=session['user_id'],Status="Completed").count()
    my_bookings = Book.query.filter_by(User_Id=session['user_id']).order_by(Book.booking_id.desc()).all()

    return render_template("user_dashboard.html",current_user=user,book_count=open_treks_count,complete_count=complete_count,booking_count=book,my_bookings=my_bookings,treks=Available_trek)

@app.route('/user/browse')
def browse():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "User":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    
    search=request.args.get("search","").strip()
    difficulty=request.args.get("difficulty")
    location=request.args.get("location")

    trek=Trek.query.filter(Trek.Status=="Open")
    if search:
        trek = trek.filter(Trek.Trek_Name.ilike(f"%{search}%"))
    if difficulty:
        trek=trek.filter(Trek.Difficulty==difficulty)
    if location:
        trek=trek.filter(Trek.Location==location)
    trek=trek.order_by(Trek.Trek_Id.desc()).all()
    locations = []
    for loc in db.session.query(Trek.Location).distinct().all():
        locations.append(loc[0])

    return render_template("user_booking.html",trek=trek,locations=locations,search=search,difficulty=difficulty)




@app.route("/user/my_bookings")
def my_bookings():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "User":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    book = Book.query.filter_by(User_Id=session["user_id"])\
                            .order_by(Book.Booking_Date.desc())\
                            .all()   
    return render_template("user_my_bookings.html",book=book)

@app.route("/book/<int:id>",methods=["POST","GET"])
def booking_trek(id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "User":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    trek=Trek.query.get_or_404(id)
    
    if trek.Status !="Open":
        flash("booking is closed")
        return redirect(url_for("browse"))
    if trek.Available_Slots<=0:
        flash("booking is closed")
        return redirect(url_for("browse"))
    already_booked=Book.query.filter_by(User_Id=user_id,Trek_Id=id,Status="Booked").first()
    if already_booked:
        flash("already booked")
        return redirect(url_for("my_bookings"))
    booking=Book(User_Id=user_id,Trek_Id=trek.Trek_Id,Status="Booked")
    trek.Available_Slots-=1
    if trek.Available_Slots == 0:
        trek.Status = "Closed"
    db.session.add(booking)
    db.session.commit()
    return redirect(url_for("my_bookings"))
    
@app.route("/user/cancel/<int:booking_id>",methods=["POST","GET"])
def cancel_booking(booking_id):
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "User":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    
    book=Book.query.get_or_404(booking_id)
    if book.User_Id != session["user_id"]:
        flash("You can only cancel your own bookings.", "danger")
        return redirect(url_for("my_bookings"))
    if book.Status!="Booked":
        flash("This booking is already cancelled or completed.", "danger")
        return redirect(url_for("my_bookings"))
    book.Status="Cancelled"
    trek = book.trek
    if trek.Available_Slots < trek.Total_Slots:
        trek.Available_Slots += 1
    if trek.Status == "Closed" and trek.Available_Slots > 0:
        trek.Status = "Open"

    db.session.commit()
    return redirect(url_for("my_bookings"))

@app.route("/user/profile",methods=["GET","POST"])
def profile():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    if session["role"] != "User":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    user=User.query.get(session['user_id'])
    if request.method=="POST":
        name=request.form.get("name")
       
        user.Username=name
      
        db.session.commit()
        return redirect(url_for("profile"))
    return render_template("user_profile.html",user=user)