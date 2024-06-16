from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=5)
app.secret_key = "poda"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class users(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(100),unique=True,nullable = False)
    password = db.Column(db.String(100) , nullable=False)
    name=db.Column(db.String(100))
    age=db.Column(db.Integer)

    def __init__(self,email,password,name = None,age=None):
        self.email=email
        self.password=password
        self.name=name
        self.age=age

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/Login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        session["email"] = email
        session["password"] = password
        find_email=users.query.filter_by(email = email).first()
        if find_email:
            find_email.password=password
        else:
            usr=users(email,password)
            db.session.add(usr)
            db.session.commit()
        flash(f"You have been logged in as {email}")
        return redirect(url_for('user'))
    else:
        if "email" in session:
            return redirect(url_for('user'))
    return render_template('login.html')  # Render the login form template

@app.route('/user', methods=["POST", "GET"])
def user():
    if "email" in session:
        email = session["email"]
        name = session.get("name", None)
        age = session.get("age", None)
        if request.method == "POST":
            name = request.form.get("name")
            age = request.form.get("age")
            if name[0].isalpha():
                session["name"] = name
                session["age"] = age
                find_email=users.query.filter_by(email = email).first()
                if find_email:
                    find_email.name=name
                    find_email.age=age
                    db.session.commit()
                flash(f"{name}, your details have been updated by {email}!")
            else:
                flash("You cant leave space in front")
        else:
            if ("name" and "age") in session:
                name=session["name"]
                age = session["age"]
        return render_template("user.html", name=name, age=age)

@app.route('/Logout')
def logout():
    session.pop("email",None)
    session.pop("password",None)
    session.pop("name",None)
    session.pop("age",None)
    flash("you have been sucessfully logged out")
    return render_template("login.html")

@app.route('/view')
def view():
    return render_template("view.html",values=users.query.all())


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
