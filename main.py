from flask import Flask,render_template,config
from models import db
app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///trekking.db'
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/login")
def login():
    return render_template("login.html")
@app.route("/register",methods=['GET','POST'])
def register():
    return render_template("register.html")


if __name__ =="__main__":
    app.run(debug=True)