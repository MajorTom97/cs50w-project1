import os
from re import search
import requests
import json
import math

from flask import Flask, session
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import login_required, api_call

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
        # user_conf = db.execute("SELECT * FROM users WHERE username = :username",{"username": username}).fetchone()
        if not request.form.get("username"):
            return render_template("error_apology.html", message="The username does not exist")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error_apology.html", message="Something went wrong with the password, check it!")

        # Query database for username
        # Check if the user alredy exists or not
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()

        # Ensure username exists and password is correct
        if rows != None:
            passw_hash = rows["hash"]
            print("---------PASSW-HASH----------")
            print(passw_hash)
            if check_password_hash(passw_hash, request.form.get("password")):
                # Remember which user has logged in
                session["user_id"] = rows[0]
                session["username"] = rows[1]
                session["logged_up"] = True

                return render_template("book_search.html")
            else:
                flash("Password does not match!!!")
                return render_template("register.html")
        else:
            # Redirect user to home page
            flash ("User does not exists!!!")
            return redirect("/register")

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
    if session["username"]:

        return render_template("book_search.html")
    else:
        return redirect("/register")

@app.route("/book_search", methods=["GET", "POST"])
@login_required
def book_search():
    """Search Page"""
    if request.method == 'GET':
        search = request.args.get("search")
        search = f"%{search}%"
        res = db.execute("SELECT * FROM books_list WHERE isbn ILIKE  :search OR title ILIKE  :search OR author ILIKE  :search", {"search":search}).fetchall()
        
        if not res:
            return render_template("error_apology.html")
    
        return render_template("book_search.html", books=res)

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
        if not db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone():
            print("-----------------------------")
            print("IN")
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
            hash_contrasena = generate_password_hash(password)

        
            # Validate per email
            # email_val = db.execute("SELECT COUNT(email) AS TOTAL FROM users WHERE email :email",{"email": email}).mappings().all()
            email_check = db.execute("SELECT * FROM users WHERE email=:email", {"email": email}).fetchone()
            
            if email_check:
                # db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone():
                flash('Email already used')
                return render_template("register.html")

            new_user = db.execute("INSERT INTO users(username, hash, email) VALUES(:username, :hash, :email) returning id_users, username",\
                                            {"username":username,
                                            "hash":hash_contrasena,
                                            "email": email
                                            }).fetchone()
            db.commit()
            print("-------------------NEW USER---------------------")
            
            print(new_user)
            session["user_id"] = new_user["id_users"]
            session["username"] = new_user["username"]
            
            print("--------------------USER_ID---------------------")
            id = session["user_id"]
            print(id)
            flash("Success!")

            # Retornar pagina de Inicio
            return redirect(url_for("login"))
        
        else:
            return redirect(url_for("login"))
    # Retornar a plantilla register, al cual usuario accede al hacer click en button register
    else:
        return render_template("register.html", message="Please register over here!")

@app.route("/data_book/<string:isbn>", methods=["GET", "POST"])
@login_required
def data_book(isbn):
    """Show the details of the book"""

    if request.method == "GET":
        
        user = session['user_id']

        review = db.execute("SELECT username, review, points FROM users JOIN reviews ON users.id_users = reviews.user_id WHERE book_isbn = :isbn", {"isbn":isbn}).fetchall()

        # Query for the details
        books = db.execute("SELECT * FROM books_list WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        print(books)

        res = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
        if res["totalItems"] > 0:
            try:
                if not 'description' in res:
                    description = res["items"][0]["volumeInfo"]["description"]
            except:
                description = "No Description"

            print(description)
            try:
                if not 'averageRating' in res:
                    average = res["items"][0]["volumeInfo"]["averageRating"]
            except:
                average = "No Average Rating"

            print(average)

            try:
                if not 'ratingsCount' in res:
                    rating = res["items"][0]["volumeInfo"]["ratingsCount"]
            except:
                rating = "No Rating Counts"

            print(rating)

            try:
                if not'publishedDate' in res:
	                published = res["items"][0]["volumeInfo"]["publishedDate"]	
            except:
                published = "No Data"
            
            try:
                if 'imageLinks' or 'smallThumbnail' in res:
                    image = res["items"][0]["volumeInfo"]["imageLinks"]["smallThumbnail"]
            except:
                image = "https://th.bing.com/th/id/R.729a2542c430580f2c22fbe68761f171?rik=HD0SAHt6cSZnnw&pid=ImgRaw&r=0"
            
            
            data_book = {
                'imageLinks': image,
                'description': description,
                'averageRating': average,
                'ratingsCount': rating,
                'publishedDate': published
            }
            return render_template("results.html", data_book=data_book, books=books, reviews=review)
        
        else:
            return render_template("error_apology.html")

            
    else:
        reviews = request.form.get("review")
        points = request.form.get("points")
        user_id = session["user_id"]
        print(reviews)
        print(points)

        query = db.execute("SELECT * FROM reviews WHERE book_isbn = :isbn AND user_id = :user_id", {"isbn" :isbn, "user_id" :user_id})

        if query.rowcount == 1:
            flash(f'You already reviewed this book')
            return redirect("/data_book/"+isbn)
        else:
            points = int(points)
            insert_rev = db.execute("INSERT INTO reviews( book_isbn, user_id, review, points) VALUES ( :isbn, :user_id, :review, :points)", {"isbn":isbn, "user_id":user_id, "review":reviews, "points": points})
            
            db.commit()
        return redirect("/data_book/"+isbn)
     

@app.route("/api/<isbn>", methods=['GET'])
def api_call(isbn):
    api_book = db.execute("SELECT * FROM books_list WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    api_rev = db.execute("SELECT COUNT(id_review) AS count, ROUND(AVG(points),2) AS point FROM reviews WHERE book_isbn = :isbn", {"isbn":isbn}).fetchone()
    print(dict(api_rev))

    if api_book == None:
        return jsonify({
            'ERROR':'Not Found'
        })

    elif api_rev == None:
        return jsonify({
            'ERROR':'Not Found'
        })
    else:
        if api_rev.point is None:
            point = 0
        else:
            point=float(api_rev.point)   
        print("---------------")
        print(api_rev)
        print(api_book)
        print("---------------")  
        print(api_book.title)
        print(api_book.author)
        print(api_book.published_yr)
        print(api_book.isbn)
        print(point)
        print(api_rev.count)

        return jsonify({
        'title': api_book.title,
        'author': api_book.author,
        'year':api_book.published_yr,
        'isbn': api_book.isbn,
        'average_score': point,
        'review_counts': api_rev.count
        })
