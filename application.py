import os

from flask import Flask, session
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        user_conf = db.execute("SELECT * FROM users WHERE username = :username",{"username": username}).fetchone()
        if not request.form.get("username"):
            return render_template("error_apology.html", message="The username does not exist")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error_apology.html", message="Something went wrong with the password, check it!")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if not len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("error_apology.html", message="Something went wrong with the password, check it!")

        # Remember which user has logged in
        session["user_id"] = user_conf[0]
        session["username"] = user_conf[1]
        session["logged_up"] = True

        # Redirect user to home page
        flash ("You were looged up!!!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", message="Login here!!!")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Olvidar cualquier registro anterior!
    session.clear()
    username = request.form.get("username")
    password = request.form.get("password")

    if user_conf = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()
    # Asegurarse de recepcionar datos por formulario!
    if request.method == "POST":

        # Si no se introduce usuario, enviar mensaje de error!
        if not request.form.get("username"):
            return render_template("error_apology.html", message="This user alredy exists!")

        # Si no se ingresa una cotraseña, enviar mensaje de error!
        elif not request.form.get("password"):
            return render_template("error_apology.html", message="You must give a password")

        # Confirmacion de Contraseña
        elif not request.form.get("confirmation"):
            return render_template("error_apology.html", message="Opsss! It seems that you forget your password")

        # Si las contraseñas no coinciden, enviar mensaje de error!
        elif not request.form.get("confirmation") == request.form.get("password"):
            return render_template("error_apology.html", message="Password does not match!")
        # Hash de Contraseña
        hash_contraseña = generate_password_hash(request.form.get("password"))

        res = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(res) != 0:
            return render_template("error_apology.html", message="The user ")

        new_user = db.execute("INSERT INTO users(username, hash) VALUES(:username, :hash)",
                                     username=request.form.get("username"),
                                     hash=hash_contraseña)

        session["user_id"] = new_user

        if not new_user:
            return render_template("error_apology.html", message="This user already exists! Try it with another username")

        flash("Success!")

        # Retornar pagina de Inicio
        return redirect(url_for("login"))

    # Retornar a plantilla register, al cual usuario accede al hacer click en button register
    else:
        return render_template("register.html", message="Please register over here!")

@app.route("/")
def index():


    return render_template("index.html")

@app.route("/api/<text:isbn>", methods=["GET"])
def api_book(isbn):

    """Call the Api from google books"""
    if request.method == 'GET':
        book=db.execute("SELECT * FROM books_list WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    
    if not book:
        return jsonify('Ohh Ohhh We did not found it!'), 403
    
    data = jsonify({
        "title": book;
        "author": book;
        "year":
        "isbn":
        "review":
        "points":
    })

    return data, 200