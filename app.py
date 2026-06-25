from flask import Flask, render_template, request, redirect, session

from flask_sqlalchemy import SQLAlchemy

from reportlab.pdfgen import canvas
app = Flask(__name__)
app.secret_key = "smartfarm"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///farm.db"

db = SQLAlchemy(app)


# =========================
# DATABASE MODELS
# =========================
class Cow(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    breed = db.Column(db.String(100))

    age = db.Column(db.String(100))

    image = db.Column(db.String(200))


class Milk(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    cowname = db.Column(db.String(100))

    liters = db.Column(db.String(100))

    date = db.Column(db.String(100))


# =========================
# CREATE DATABASE
# =========================

with app.app_context():

    db.create_all()


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home(): 
    if "user" not in session:

        return redirect("/login")

    search = request.args.get("search")

    if search:

        cows = Cow.query.filter(

            Cow.name.contains(search)

        ).all()

    else:

        cows = Cow.query.all()

    milks = Milk.query.all()

    total_milk = 0

    milk_price = 50

    total_income = total_milk * milk_price

    for milk in milks:

        total_milk += int(milk.liters)

    return render_template(

    "home.html",

    cows=cows,

    total_milk=total_milk,

    total_income=total_income,

    milks=milks

)


# =========================
# ADD COW PAGE
# =========================

@app.route("/addcow")
def addcow():

    return render_template("addcow.html")


# =========================
# SAVE COW
# =========================

@app.route("/savecow", methods=["POST"])
def savecow():

    cowname = request.form.get("cowname")

    breed = request.form.get("breed")

    age = request.form.get("age")

    image = request.files["image"]

    image_path = "static/uploads/" + image.filename

    image.save(image_path)

    new_cow = Cow(

        name=cowname,

        breed=breed,

        age=age,

        image="/" + image_path

    )

    db.session.add(new_cow)

    db.session.commit()

    return redirect("/")


# =========================
# DELETE COW
# =========================

@app.route("/delete/<id>")
def delete(id):

    cow = Cow.query.get(id)

    db.session.delete(cow)

    db.session.commit()

    return redirect("/")


# =========================
# EDIT COW PAGE
# =========================

@app.route("/edit/<id>")
def edit(id):

    cow = Cow.query.get(id)

    return render_template("edit.html", cow=cow)


# =========================
# UPDATE COW
# =========================

@app.route("/update/<id>", methods=["POST"])
def update(id):

    cow = Cow.query.get(id)

    cow.name = request.form.get("cowname")

    cow.breed = request.form.get("breed")

    cow.age = request.form.get("age")

    db.session.commit()

    return redirect("/")


# =========================
# ADD MILK PAGE
# =========================

@app.route("/addmilk")
def addmilk():

    return render_template("addmilk.html")


# =========================
# SAVE MILK
# =========================

@app.route("/savemilk", methods=["POST"])
def savemilk():

    cowname = request.form.get("cowname")

    liters = request.form.get("liters")

    date = request.form.get("date")

    new_milk = Milk(

        cowname=cowname,

        liters=liters,

        date=date

    )

    db.session.add(new_milk)

    db.session.commit()

    return redirect("/")


# =========================
# LOGIN PAGE
# =========================

@app.route("/login", methods=["GET", "POST"])

def login():

    if request.method == "POST":

        username = request.form.get("username")

        password = request.form.get("password")

        if username == "admin" and password == "1234":

            session["user"] = username

            return redirect("/")

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================
# RUN APP
# =========================
@app.route("/report")
def report():

    cows = Cow.query.all()

    milks = Milk.query.all()

    pdf = canvas.Canvas("report.pdf")

    pdf.drawString(

        100,

        800,

        "SMART DAIRY FARM REPORT"

    )

    pdf.drawString(

        100,

        760,

        f"Total Cows : {len(cows)}"

    )

    total = 0

    for milk in milks:

        total += int(milk.liters)

    pdf.drawString(

        100,

        720,

        f"Total Milk : {total} Liters"

    )

    pdf.save()

    return "PDF Report Generated 😎"
if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)