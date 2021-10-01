# @app.route("/book_search/<text:isbn>", methods=["GET", "POST"])
# @login_required
# def data_book(isbn):
#     """Show the details of the book"""

#     if request.method == "GET":
        
#         user = session['user_id']
        
#         # Query for the details
#         book = db.execute("SELECT books_list WHERE isbn LIKE = :isbn", {"isbn": isbn}).fetchone()

#         # Ratings details
#         rating_count = db.execute("SELECT COUNT(points), AVG(points) FROM ((reviews JOIN books_list on reviews.book_isbn = book_isbn) JOIN users ON reviews.user_id = users.id_users ) WHERE books_list.isbn = :book", {"book": book['isbn']}).fetchone()

#         comments = db.execute("SELECT COUNT(review) FROM ((reviews JOIN books_list on reviews.book_isbn = books_list.isbn) JOIN users ON reviews.user_id = users.id_users) WHERE books_list.isbn = :book AND reviews.comments != '' ", {"book":book['isbn']}).fetchone()

#         query_book = db.execute('SELECT book_isbn FROM books_list WHERE isbn = :isbn',{"isbn":isbn})

#         data = query_book.fetchone()
#         book = data[0]

#         review = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_isbn = :book_isbn", {"user_id": user, "book_isbn": book})

#         if review.rowcount == 1:
#             flash("You already reviewed this book")
#             return render_template("data_book.html")



# query_book = db.execute('SELECT book_isbn FROM books_list WHERE isbn = :isbn',{"isbn":isbn})

        # data = query_book.fetchone()
        # book = data[0]

        # review = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_isbn = :book_isbn", {"user_id": user, "book_isbn": book})

        # if book.rowcount == 1:
        #     flash("You already reviewed this book")
        #     return render_template("data_book.html")