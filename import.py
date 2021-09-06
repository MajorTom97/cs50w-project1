import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, published_yr in reader:
        db.execute("INSERT INTO books_list (isbn, title, author, published_yr) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": published_yr})
        print(f"Added book from to {isbn} {title} {author} and {published_yr}.")
    db.commit()

if __name__ == "__main__":
    main()