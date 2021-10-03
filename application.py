import os
import requests
import json

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
        user_conf = db.execute("SELECT * FROM users WHERE username = :username",{"username": username}).fetchone()
        if not request.form.get("username"):
            return render_template("error_apology.html", message="The username does not exist")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error_apology.html", message="Something went wrong with the password, check it!")

        # Query database for username
        # Check if the user alredy exists or not
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()

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

            
            # Validate per email
            email_val = db.execute("SELECT COUNT(email) AS TOTAL FROM users WHERE email :email",{"email": email}).mappings().all()
            
            if db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone():

                try:

                    new_user = db.execute("INSERT INTO users(username, hash, email) VALUES(:username, :hash, :email) returning id_users, username, hash, email",
                                            {"username":request.form.get("username"),
                                            "hash":hash_contraseña,
                                            "email":request.form.get("email")
                                            }).fetchone()
                    db.commit()

                    print(new_user)
                    session["user_id"] = new_user["id_users"]
                    session["username"] = new_user["username"]
                    username=session["username"]
            
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

@app.route("/book_search/<string:isbn>", methods=["GET", "POST"])
@login_required
def data_book(isbn):
    """Show the details of the book"""

    if request.method == "GET":
        
        user = session['user_id']

        review = db.execute("SELECT username, review, points FROM users JOIN reviews ON users.user_id = reviews.user_id WHERE isbn = :isbn", {"isbn":isbn}).fetchall()

        # Query for the details
        book = db.execute("SELECT books_list WHERE isbn LIKE = :isbn", {"isbn": isbn}).fetchone()
        print(book)

        res = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
        
    else:
        reviews = request.form.get("review")
        points = request.form.get("points")
        user_id = session["user_id"]
        print(reviews)
        print(points)

        query = db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND user_id = :user_id", {"isbn" :isbn, "user_id" :user_id})

        if query.rowcount == 1:
            flash(f'You already reiwed this book')
            return redirect("/data_book/"+isbn)
        else:
            points = int(points)
            insert_rev = db.execute("INSERT INTO reviews(user_id, isbn, review, points) VALUES (:user_id, :isbn, :review, :points)", {"user_id":user_id,"isbn":isbn, "review":reviews, "points": points})

            db.commit()
        return redirect("/data_book/"+isbn)

@app.route("/book_search/<string:type>", methods=["POST"])
@login_required
def results(isbn):
    """Search Results"""
    if request.method == 'POST':

            # Result for search
            res = db.execute("SELECT isbn, title, author FROM books_list WHERE isbn = :isbn", {"isbn": isbn}).fetchmany()

            if res:
                search = f'Match by ISBN "{isbn}"'
                return render_template("book_search.html")
            
            elif not res:
                #query for a partial result on the database
                query = '%' + isbn + '%'

                coincidences = db.execute("SELECT * FROM books_list WHERE isbn LIKE :isbn ORDER BY isbn", {"isbn" :query}).fetchmany()

                match_res = db.execute("SELECT COUNT (*) FROM books_list WHERE isbn LIKE :isbn ORDER BY isbn", {"isbn" :query}).fetchone()
                match_res = match_res[0]

                if not query:
                    search = f'No matches for "{isbn}"'
                    return render_template("results.html")

            elif type == 'title':
                title = request.form.get('title')
                # Result for search
                res = db.execute("SELECT * FROM books_list WHERE UPPER (title) = :title", {"title": title.upper()}).fetchmany()

                if res:
                    search = f'Match by Title "{title}"'
                    return render_template("book_search.html")
                
                elif not res:
                    #query for a partial result on the database
                    query = '%' + title + '%'

                    coincidences = db.execute("SELECT * FROM books_list WHERE UPPER (title) LIKE :title ORDER BY title", {"title" :query.upper()}).fetchmany()

                    match_res = db.execute("SELECT COUNT (*) FROM books_list WHERE title LIKE :title ORDER BY title", {"title" :query}).fetchone()
                    match_res = match_res[0]

                    if not query:
                        search = f'No matches for "{title}"'
                        return render_template("results.html")

            elif type == 'author':

                author = request.form.get('author')
                # Result for search
                res = db.execute("SELECT * FROM books_list WHERE UPPER (author) = :author", {"author": author.upper()}).fetchmany()

                if res:
                    search = f'Match by Author "{author}"'
                    return render_template("book_search.html")
                
                elif not res:
                    #query for a partial result on the database
                    query = '%' + author + '%'

                    coincidences = db.execute("SELECT * FROM books_list WHERE UPPER (author) LIKE :author ORDER BY author", {"author" :query.upper()}).fetchmany()

                    match_res = db.execute("SELECT COUNT (*) FROM books_list WHERE title LIKE :author ORDER BY author", {"author" :query}).fetchone()
                    match_res = match_res[0]

                    if not query:
                        search = f'No matches for "{author}"'
                        return render_template("results.html") 

                elif type == 'published_yr':

                    published_yr = request.form.get('published_yr')
                    # Result for search
                    res = db.execute("SELECT * FROM books_list WHERE UPPER (published_yr) = :published_yr", {"published_yr": published_yr.upper()}).fetchmany()

                    if res:
                        search = f'Match by published_yr "{published_yr}"'
                        return render_template("book_search.html")
                    
                    elif not res:
                        #query for a partial result on the database
                        query = '%' +published_yr + '%'

                        coincidences = db.execute("SELECT * FROM books_list WHERE UPPER (published_yr) LIKE :published_yr ORDER BY published_yr", {"published_yr" :query.upper()}).fetchmany()

                        match_res = db.execute("SELECT COUNT (*) FROM books_list WHERE published_yr LIKE :published_yr ORDER BY published_yr", {"published_yr" :query}).fetchone()
                        match_res = match_res[0]

                        if not query:
                            search = f'No matches for "{published_yr}"'
                            return render_template("results.html") 
    else:
        return render_template("book_search.html")
    flash("Something went wrong")       


@app.route("/api/<isbn>", methods=['GET'])
def api_call(isbn):
    api_book = db.execute("SELECT * FROM books_list WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    api_rev = db.execute("SELECT id_review, points FROM reviews WHERE isbn = :isbn", {"isbn":isbn}).fetchone()

    if api_book == None:
        flash(f"Something went wrong!")

    elif api_rev == None:
        flash(f'Something went wrong!')

    print(api_book.title)
    print(api_book.author)
    print(api_book.published_yr)
    print(api_book.isbn)
    print(api_book.points)
    print(api_book.reviews)
    # else:
    #     return jsonify({
    #     'title': api_book.title,
    #     'author': api_book.author,
    #     'year':api_book.published_yr,
    #     'isbn': api_book.isbn,
    #     'average_score': api_book.points,
    #     'review_counts': api_book.reviews
    #     })
