from __future__ import absolute_import
# myapp/models.py

from flask.ext.sqlalchemy import SQLAlchemy

from myapp import app

# Creating and initializing the database object on separate lines to make sure
# that Flask-Fixtures works when there's currently no app/request context
# (Issue #22).
db = SQLAlchemy()
db.init_app(app)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    published_date = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship('Author', backref='books')
