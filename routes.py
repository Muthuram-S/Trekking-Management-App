
from app import app
from flask import render_template,request,session,url_for,redirect,flash
from werkzeug.security import check_password_hash,generate_password_hash
from models import db,User,Trek,Book


@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')
        
        user=User.query.filter_by(Email=email).first()

        if user and check_password_hash(user.Password,password):
            if user.Status=="Blacklisted":
                return redirect(url_for("login"))
            session["user_id"]=user.Id
            session["role"]=user.Role
          
        else:
            return "invalid credentials"
        
        
            
            return redirect(url_for("staff_dashboard"))
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

        exist_user=User.query.filter_by(Email=email).first()

        error=[]

        if not name:
            error.append("Name is required")
        if "@" not in email:
            error.append("Invalid email")
        if len(password)<6:
            error.append("Password must be at least 6 character long")
        if password!=confirm_password:
            error.append("password do not match")
        if User.query.filter_by(Email=email).first():
            error.append("This email is already exist")

        if error:
            for i in error:
                flash(i,"danger")
                return render_template("Register.html", form=request.form)
        if role=='Staff':
            status='Pending'
        else:
            status='Approved'
        if exist_user:
            flash("Email already exists", "danger")
            return redirect(url_for("register"))

        hash_password=generate_password_hash(password)
        if not password == confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("register"))

        new_user=User(Username=name,Email=email,Password=hash_password,Role=role,Status=status)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/admin')
def admin():
    user=User.query.filter_by(Role="User").count()
    staff=User.query.filter_by(Role="Staff").count()
    bookings=Book.query.count()
    trek=Trek.query.count()
    return render_template("admin.html",count_user=user,count_staff=staff,trek=trek,total_bookings=bookings)
@app.route('/admin/edit_trek/<int:trek_id>',methods=['GET','POST'])
@app.route("/add_trek/",methods=['GET','POST'])

def add_trek(trek_id=None):
    staffs=User.query.filter_by(Role='Staff').all()
    trek=Trek.query.filter_by(Trek_Id=trek_id).first()
    if request.method=="POST":
        
        from datetime import datetime 
        start_date=datetime.strptime(request.form.get('start_date'),"%Y-%m-%d").date()
        end_date=datetime.strptime(request.form.get('end_date'),"%Y-%m-%d").date()
        duration=(end_date-start_date).days
        Trek_Name=request.form.get('trek_name')
        Location=request.form.get('location')
        Difficulty=request.form.get('difficulty')
        Total_Slots=int(request.form.get('total_slots'))
        Price=int(request.form.get('price'))
        Staff_Id=request.form.get("staff_id") or None
        status = request.form.get("status")
        Available_Staff=Total_Slots
        Description=request.form.get('description')
        Start_Date = start_date
        End_Date = end_date
        Duration=duration
        if trek:
            trek.Trek_Name = Trek_Name
            trek.Location = Location
            trek.Difficulty = Difficulty
            trek.Total_Slots = Total_Slots
            trek.Price = Price
            trek.Staff_Id = Staff_Id
            trek.Description = Description
            trek.Start_Date = Start_Date
            trek.End_Date = End_Date
            trek.Duration = Duration
            trek.Status = status
        else:
            new_trek=Trek(Trek_Name=Trek_Name,Location=Location,
            Difficulty=Difficulty,Total_Slots=Total_Slots,
            Price=Price,Start_Date=Start_Date,Description=Description,Staff_Id = Staff_Id,Available_Staff=Available_Staff,
            End_Date=End_Date,Status="Pending")
            db.session.add(new_trek)
        db.session.commit()
        flash('Trek added successfully!', 'success')
        return redirect(url_for('trek'))
    return render_template('add_Trek.html',staffs=staffs,trek=trek)

# @app.route('/admin/edit_trek/<int:trek_id>')
# def edit_trek(trek_id):
#     trek=Trek.query.filter_by(Trek_Id=trek_id)
#     return redirect(url_for('add_trek',trek=trek))


@app.route("/admin/user_management")
@app.route("/admin/user_management/<int:user_id>")
def user_management(user_id=None):
    user = User.query.filter_by(Role="User").all()
    selected_user = None
    booking_count = 0

    if user_id:
        selected_user = User.query.get(user_id)

        if selected_user:
            booking_count = Book.query.filter_by(User_Id=user_id).count()
    return render_template(
        "admin_user_management.html",
        booking_count=booking_count,user=user
    )

@app.route("/admin/staff_management")

def staff_management():
    staff = User.query.filter_by(Role="Staff").all()

    staff_dt=[]
    for i in staff:
        trek=Trek.query.filter_by(Staff_Id=i.Id).first()
        staff_dt.append({
            "trek":trek,
            "staff":i
                            })

    return render_template(
        "admin_staff_management.html",
        staff_dt=staff_dt
    )
@app.route("/admin/blacklist/<int:staff_id>")
def blacklist(staff_id):
    staff=User.query.filter_by(Id=staff_id).first()
    if not staff:
        flash("staff is not found","danger")
        return redirect(url_for("admin_staff_management"))
    staff.status="Blacklisted"
    db.session.commit()
    flash("staff has been blacklisted","danger")
    return redirect(url_for("admin_staff_management"))
@app.route("/admin/approve/<int:staff_id>")
def approve(staff_id):
    staff=User.query.filter_by(Id=staff_id).first()
    if not staff:
        flash("staff is not found","danger")
        return redirect(url_for("admin_staff_management"))
    staff.status="Approved"
    db.session.commit()
    flash("staff has been Approved","success")
    return redirect(url_for("admin_staff_management"))

@app.route("/admin/trek")
def trek():
    trek=Trek.query.order_by(Trek.Trek_Id.desc()).all()
    
    return render_template("admin_trek.html",trek=trek)

@app.route("/admin/bookings")
def bookings():
    book=Book.query.all()
    return render_template("admin_booking.html",book=book)

@app.route("/admin/delete/<int:trek_id>", methods=["POST"])
def delete(trek_id):
    delete_trek = Trek.query.get_or_404(trek_id)
    db.session.delete(delete_trek)
    db.session.commit()
    
    return redirect(url_for("trek"))


@app.route("/staff/dashboard")
def staff_dashboard():
    staff_id=session["user_id"]
    trek=Trek.query.filter_by(Staff_Id=staff_id).all()
    return redirect(url_for("staff_dashboard",trek=trek))
@app.route("/staff/update_trek/<int:trek_id>",methods=['GET','POST'])
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if request.method == "POST":
        trek.Total_Slots=request.form.get("available_slots")
        trek.Status=request.form.get("status")
        db.session.commit()
    return render_template("staff_dashboard")


@app.route("/staff/participants/<int:trek_id>")
def participants(trek_id):
    book=Book.query.filter_by(Trek_Id=trek_id).all()
    trek = Trek.query.get_or_404(trek_id)
    
    return render_template("staff_participants.html",trek=trek,book=book)

