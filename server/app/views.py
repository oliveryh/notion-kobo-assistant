from flask import render_template, request

from app import app, db
from app.imports import refresh as refresh_books
from app.imports import convert_url_to_keypub
from app.models import Author, Book


@app.route("/", methods=["GET"])
def home():
    books = db.session.query(Book).order_by(Book.created_at.desc()).all()
    books_list = []

    for book in books:
        author = Author.query.get(book.author_id)
        book_object = {
            "id": book.book_id,
            "title": book.title,
            "author": author.name,
            "filename": book.filename,
            "url": book.url,
        }
        books_list.append(book_object)

    return render_template("index.html", books=books_list)


@app.route("/refresh", methods=["POST"])
def refresh():

    refresh_books()
    return {}


@app.route("/submit", methods=["POST"])
def submit():

    url = request.form["url"]
    book = convert_url_to_keypub(url)

    response = f"""
    <tr>
        <td>{book.title}</td>
        <td>{book.author.name}</td>
        <td><a href="{book.url}">Link</a></td>
        <td><a href="p-api/{book.filename}">Download</a></td>
    </tr>
    """
    return response
