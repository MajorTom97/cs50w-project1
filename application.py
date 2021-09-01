import os

from flask import Flask, session
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Olvidar cualquier registro anterior!
    session.clear()

    # Asegurarse de recepcionar datos por formulario!
    if request.method == "POST":

        # Si no se introduce usuario, enviar mensaje de error!
        if not request.form.get("username"):
            return apology("Debes Ingresar un Usuario", 400)

        # Si no se ingresa una cotraseña, enviar mensaje de error!
        elif not request.form.get("password"):
            return apology("Ingresar una Contraseña", 400)

        # Confirmacion de Contraseña
        elif not request.form.get("confirmation"):
            return apology("Contraseñas no coinciden!", 400)

        # Si las contraseñas no coinciden, enviar mensaje de error!
        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("Contraseña Incorrecta", 400)
        # Hash de Contraseña
        hash_contraseña = generate_password_hash(request.form.get("password"))

        res = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(res) != 0:
            return apology("Este usuario ya existe!")

        nuevo_idUsuario = db.execute("INSERT INTO users(username, hash) VALUES(:username, :hash)",
                                     username=request.form.get("username"),
                                     hash=hash_contraseña)

        session["user_id"] = nuevo_idUsuario

        if not nuevo_idUsuario:
            return apology("Ya existe este Usuario!")

        flash("Registro Exitoso!")

        # Retornar pagina de Inicio
        return redirect(url_for("index"))

    # Retornar a plantilla register, al cual usuario accede al hacer click en button register
    else:
        return render_template("register.html")

@app.route("/")
def index():


    return render_template("index.html")
