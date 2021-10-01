import csv
import urllib.request
import requests
import pprint

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def api_call(isbn):
    
    #isbn = '0473235501'
    response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
    print("----------------------------------------")
    pprint.pprint(response)
    data_book = {
        'title': 'No Description',
        'authors': 'No Description',
        'years':'No Description',
        'description': 'No Description',
        'averageRating': 'No Description',
        'ratingsCount': 'No Description',
        'thumbnails': 'No Description'
    }
    try:
        img=response["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]    
        data_book["thumbnails"]=img

        volume=response["items"][0]["volumeInfo"]

        if not volume:
	        print("no nos llego datos")
    except:
        print("lol")
    
    #////////////////////////////////////////////////
    try:
        if not 'ratingsCount' in response:
	 
	        data_book["ratingsCount"]=volume["ratingsCount"]
	        print(data_book)
    except:
        data_book["ratingsCount"]="No Description"
        pprint.pprint(data_book)

	 #////////////////////////////////////////////////
    try:

        if not 'averageRating' in response:

	    		 
	        data_book["averageRating"]=volume["averageRating"]
	        print(data_book)	 
    except:
        data_book["averageRating"]="No Description"
        pprint.pprint(data_book)
	
     #////////////////////////////////////////////////
    
    try:
        if  not 'authors' in response:

	 
	        data_book["authors"]=volume["authors"]
	        print(data_book)	 
    except:
        data_book["authors"]="No Description"
        pprint.pprint(data_book)
    
     #////////////////////////////////////////////////
    try:
        if not 'title' in response:


	        data_book["title"]=volume["title"]
	        print(data_book)	 
    except:
        data_book["title"]="No Description"
        pprint.pprint(data_book)
        
     #////////////////////////////////////////////////
    try:
        if not'publishedDate' in response:

	 		 
	        data_book["years"]=volume["publishedDate"]
	        print(data_book)	
    except:

        data_book["years"]="No Description"
        pprint.pprint(data_book)
        
      #////////////////////////////////////////////////
    try :
        if not 'description' in response:


		 
	        data_book["description"]=volume["description"]
	        
    except:
        data_book["description"]="No Description"
    print("00000000000000000000000000000000000000000000000000")
    pprint.pprint(data_book)
    return data_book
    print("00000000000000000000000000000000000000000000000000")

