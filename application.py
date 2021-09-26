import os
import requests
import json

from flask import Flask, session
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import login_required

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

        username = request.form.get("username")
        # Ensure username was submitted
        user_conf = db.execute("SELECT * FROM users WHERE username = :username",{"username": username}).fetchone()
        if not request.form.get("username"):
            return render_template("error_apology.html", message="The username does not exist")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error_apology.html", message="Something went wrong with the password, check it!")

        # Query database for username
        # Check if the user alredy exists or not
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount()

        # Ensure username exists and password is correct
        if not len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("error_apology.html", message="Something went wrong, check it!")

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

@app.route("/")
@login_required
def index():
    """Loads index page with the search box"""
    return render_template("index.html")

@app.route("/book_search", methods=["GET", "POST"])
@login_required
def book_search():
    """Search Page"""
    return render_template("book_search.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Olvidar cualquier registro anterior!
    session.clear()
    
    # Asegurarse de recepcionar datos por formulario!
    if request.method == "POST":
    
        # Data from the user
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

    #Check if an username already exists
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone():
        
        if not request.form.get("email"):
            return render_template("error_apology.html", message="Opsss! You must provide an email account!")

        # Si no se introduce usuario, enviar mensaje de error!
        if not request.form.get("username"):
            return render_template("error_apology.html", message="You must bring an username!")

        # Si no se ingresa una cotraseña, enviar mensaje de error!
        elif not request.form.get("password"):
            return render_template("error_apology.html", message="You must bring a password")

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
            return render_template("error_apology.html", message="The user already exists")
        
        # Validate per email
        email_val = db.execute("SELECT COUNT(email) AS TOTAL FROM users WHERE email :email",{"email": email}).mappings().all()
        
        if email_val[0]["total"] == 1:

            try:

                new_user = db.execute("INSERT INTO users(username, password, confirmation, email, hash) VALUES(:username, :password, :confirmation, :email, :hash)",
                                        username=request.form.get("username"),
                                        username=request.form.get("password"),
                                        username=request.form.get("confirmation"),
                                        username=request.form.get("email"),
                                        hash=hash_contraseña)
                print(new_user)
                session["user_id"] = dict(new_user.fetchone())["id_users"]
                session["username"] = username
                username=session["username"]
                print("Credentials are: ", len(new_user))
                for row in new_user:
                    print("ID: ", row[0])
                    print("username: ", row[1])
                    print("email: ", row[4])
        
            except Exception as err:
                print(err)
                flash("This user already exists! Try it with another username")

        if not new_user:
            return render_template("error_apology.html")

        flash("Success!")

        # Retornar pagina de Inicio
        return redirect(url_for("login"))

    # Retornar a plantilla register, al cual usuario accede al hacer click en button register
    else:
        return render_template("register.html", message="Please register over here!")

@app.route("/book_search/<text:isbn>", methods=["GET", "POST"])
@login_required
def data_book(isbn):
    """Show the details of the book"""

    if request.method == "GET":
        
        # Query for the details
        book = db.execute("SELECT books_list WHERE isbn LIKE = :isbn", {"isbn": isbn}).fetchone()

        # Ratings details
        rating_count = db.execute("SELECT COUNT(points), AVG(points) FROM ((reviews JOIN books_list on reviews.book_isbn = book_isbn) JOIN users ON reviews.user_id = users.id_users ) WHERE books_list.isbn = :book", {"book": book['isbn']}).fetchone()

        comments = db.execute("SELECT COUNT(review) FROM ((reviews JOIN books_list on reviews.book_isbn = books_list.isbn) JOIN users ON reviews.user_id = users.id_users) WHERE books_list.isbn = :book AND reviews.comments != '' ", {"book":book['isbn']}).fetchone()

        if not rating_count[0] == 0:
            

@app.route("/api/<text:isbn>", methods=["GET"])
def api_book(isbn):

    """Call the Api from google books"""
    if request.method == 'GET':
        book=db.execute("SELECT * FROM books_list WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    if not book:
        return jsonify('Ohh Ohhh We did not found it!'), 403
    
    #Goodreads data
    route = request.get("https://www.goodreads.com/book/review_counts.json", params={"key": GOODREADS_API_KEY, "isbn":book_isbn})
    if route != 200:
        raise Exception("ERROR: API request unsuccessful!")
    data = route.json

    if data['books_list'][0]['ratings_count'] == 0 or not data['books'][0]['work_ratings_count']:
        data['books_list'][0]['average_rating'] = "None"  
    
    return  jsonify({
        "title": book.title;
        "author": book.author;
        "year": book.year;
        "isbn": book.isbn;
        "review": data["books_list"][0]['ratings_count'],
        "points": data['books_list'][0]['average_rating']
    })

