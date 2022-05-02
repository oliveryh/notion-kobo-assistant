from flask import render_template, request

from app import app, db
from app.imports import refresh as refresh_books
from app.imports import convert_url_to_keypub
from app.models import Author, Book

data = [
    {"title": "Harry", "author": "JK Rowling"},
    {"title": "Lord of Rings", "author": "Whoever"},
]


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


@app.route("/get-book-row/<int:id>", methods=["GET"])
def get_book_row(id):
    book = Book.query.get(id)
    author = Author.query.get(book.author_id)

    response = f"""
    <tr>
        <td>{book.title}</td>
        <td>{author.name}</td>
    </tr>
    """
    return response


@app.route("/get-edit-form/<int:id>", methods=["GET"])
def get_edit_form(id):
    book = Book.query.get(id)
    author = Author.query.get(book.author_id)

    response = f"""
    <tr hx-trigger='cancel' class='editing' hx-get="/get-book-row/{id}">
  <td><input name="title" value="{book.title}"/></td>
  <td>{author.name}</td>
  <td>
    <button class="btn btn-primary" hx-get="/get-book-row/{id}">
      Cancel
    </button>
    <button class="btn btn-primary" hx-put="/update/{id}" hx-include="closest tr">
      Save
    </button>
  </td>
</tr>
    """
    return response


@app.route("/update/<int:id>", methods=["PUT"])
def update_book(id):
    db.session.query(Book).filter(Book.book_id == id).update(
        {"title": request.form["title"]}
    )
    db.session.commit()

    title = request.form["title"]
    book = Book.query.get(id)
    author = Author.query.get(book.author_id)

    response = f"""
    <tr>
        <td>{title}</td>
        <td>{author.name}</td>
    </tr>
    """
    return response


@app.route("/delete/<int:id>", methods=["DELETE"])
def delete_book(id):
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()

    return ""


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
