from datetime import datetime

from flask_sqlalchemy.model import DefaultMeta

from app import db

BaseModel: DefaultMeta = db.Model


class Author(BaseModel):
    author_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    books = db.relationship("Book", backref="author")

    def __repr__(self):
        return '<Author: {}>'.format(self.books)


class Book(BaseModel):
    book_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("author.author_id"))
    title = db.Column(db.String)
    filename = db.Column(db.String)
    url = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
