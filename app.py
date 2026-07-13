from flask import Flask,render_template,config,request,redirect,url_for,flash,session
from models import db,User,Trek
from werkzeug.security import generate_password_hash,check_password_hash

app=Flask(__name__)

import sys
sys.modules['app'] = sys.modules[__name__]

import routes.auth
import routes.admin
import routes.staff
import routes.user


app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///trekking.db'
app.config['SECRET_KEY']='mysecretkey'
db.init_app(app)

with app.app_context():
    db.create_all()

    if not User.query.filter_by(Role="Admin").first():
        admin = User(
            Username="Admin",
            Email="admin@gmail.com",
            Password=generate_password_hash("admin123"),
            Role="Admin",
            Status="Approved"
        )
        db.session.add(admin)
        db.session.commit()

if __name__ =="__main__":
    app.run(debug=True)