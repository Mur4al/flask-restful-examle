from typing import List

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

book_author = db.Table('book_author',
                       db.Column('author_id', db.Integer, db.ForeignKey('author.author_id'), primary_key=True),
                       db.Column('book_id', db.Integer, db.ForeignKey('book.book_id'), primary_key=True)
                       )


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    refresh_token = db.Column(db.Text)

    def __init__(self, username: str, password: str):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def save(self):
        db.session.add(self)
        db.session.commit()


class Author(db.Model):
    author_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    portrait = db.Column(db.String(255), nullable=True)

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    cover_image = db.Column(db.String(255), nullable=True)
    authors = db.relationship('Author', secondary=book_author, lazy='subquery',
                              backref=db.backref('books', lazy=True))

    def __init__(self, name: str, authors: List = None):
        self.name = name
        if authors:
            self.authors = Author.query.filter(Author.author_id.in_(authors)).all()

    def update_authors(self, authors: List):
        self.authors = Author.query.filter(Author.author_id.in_(authors)).all()

    def __str__(self):
        return self.name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
