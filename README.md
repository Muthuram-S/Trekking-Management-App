# TrekManager - Trekking Management Application

## Project Overview

TrekManager is a web-based Trekking Management Application developed using **Flask**, **SQLAlchemy ORM**, **SQLite**, **Jinja2**, and **Bootstrap 5**. The application manages trekking activities through three different user roles:

- Admin
- Trek Staff
- User (Trekkers)

The project was developed as part of the **Modern Application Development I (MAD-I)** course.

---

## Features

### Admin
- Secure Login
- Dashboard with statistics
- Add, Edit and Delete Treks
- Approve / Blacklist Staff
- Approve / Blacklist Users
- Assign Staff to Treks
- View Bookings
- Manage Users
- Manage Staff

### Trek Staff
- Register and Login
- Update Profile
- View Assigned Treks
- Update Trek Status
- Update Available Slots
- View Registered Participants

### User
- Register and Login
- Update Profile
- Browse Available Treks
- Search Treks
- Book Trek
- Cancel Booking
- View Booking History

---

## Technologies Used

- Python 3.x
- Flask
- SQLAlchemy ORM
- SQLite
- HTML5
- CSS3
- Bootstrap 5
- Jinja2

---

## Project Structure

```
Trekking-Management-App/
│
├── app.py
├── models.py
├── requirements.txt
├── README.md
├── trekking.db
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── admin.html
│   ├── staff_dashboard.html
│   ├── user_dashboard.html
│   └── ...
│
├── static/
│   ├── css/
│   ├── images/
│   └── ...
```

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Trekking-Management-App
```

### 2. Create Virtual Environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

Run the Flask application:

```bash
python app.py
```

Open your browser and visit

```
http://127.0.0.1:5000
```

---

## Database

The application uses a single SQLite database.

Database file:

```
trekking.db
```

The database contains three tables:

- User
- Trek
- Book

The Admin account is created programmatically during database initialization.

---

## Default Admin Login

```
Email:
admin@gmail.com

Password:
admin123
```

(Change according to your implementation.)

---

## Dependencies

Install all required packages using

```bash
pip install -r requirements.txt
```

Example packages include:

- Flask
- Flask-SQLAlchemy
- Werkzeug

---

## Author

Muthuram S.


IIT Madras BS Degree Programme
