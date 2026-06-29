from flask_sqlalchemy import SQLAlchemy

from datetime import datetime as dt
db=SQLAlchemy()

class User(db.Model):
    Id=db.Column(db.Integer,primary_key=True)
    Username=db.Column(db.String(100),unique=False,nullable=False)
    Email=db.Column(db.String(100),unique=True,nullable=False)
    Password=db.Column(db.String(100),unique=False,nullable=False)
    Role=db.Column(db.String(100),nullable=False)
    Status=db.Column(db.String(100),nullable=False)
    bookings=db.relationship('Book',backref='user')

class Trek(db.Model):
    Trek_Id=db.Column(db.Integer,primary_key=True,nullable=False)
    Trek_Name=db.Column(db.String(100),nullable=False)
    Location=db.Column(db.String(100),nullable=False)
    Duration=db.Column(db.Integer,nullable=False)
    Difficulty=db.Column(db.String(100),nullable=False)
    Price=db.Column(db.Integer,nullable=False)
    Total_Slots=db.Column(db.Integer,nullable=False)
    Staff_Id=db.Column(db.Integer,db.ForeignKey('user.Id'),nullable=True)
    Status=db.Column(db.String(100),nullable=False)
    Start_Date=db.Column(db.Date,nullable=False)
    End_Date=db.Column(db.Date,nullable=False)
    Description=db.Column(db.Text,nullable=False)
    bookings=db.relationship('Book',backref='trek')
    Available_Staff=db.Column(db.Integer,nullable=False)
    staff = db.relationship('User', foreign_keys=[Staff_Id])

class Book(db.Model):
    booking_id=db.Column(db.Integer,primary_key=True)
    User_Id=db.Column(db.Integer,db.ForeignKey('user.Id'),nullable=False)
    Trek_Id=db.Column(db.Integer,db.ForeignKey('trek.Trek_Id'),nullable=False)
    Booking_Date=db.Column(db.DateTime,nullable=False,default=dt.now)
    Status=db.Column(db.String(100),nullable=False)