from flask import Flask,render_template,config,request,redirect,url_for,flash,session
from models import db,User
from werkzeug.security import generate_password_hash,check_password_hash
app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///trekking.db'
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email=request.form.get('')
        password=request.form.get('')
        
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            session["user_id"]=user.id
            session["role"]=user.role
            return redirect(url_for('home'))
        else:
            return "invalid credentials"
    else:
        return render_template('login.html')


    return render_template("login.html")
@app.route("/register",methods=['GET','POST'])
def register():
    if request.method =='POST':
        name=request.form.get('')
        email=request.form.get('')
        password=request.form.get('')
        role=request.form.get('')

        exist_user=User.query.filter_by(email=email).first()
        if role=='staff':
            status='Pending'
        else:
            status='Approved'
        if exist_user:
            return "this email is aldready exist"
        hash_password=generate_password_hash(password)
        new_user=User(name=name,email=email,password=hash_password,role=role,status=status)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

if __name__ =="__main__":
    app.run(debug=True)