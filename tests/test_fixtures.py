# myapp/fixtures/test_fixtures.py

import unittest

from myapp import app
from myapp.models import db, Book, Author

from flask.ext.fixtures import FixturesMixin

# Configure the app with the testing configuration
app.config.from_object('myapp.config.TestConfig')

# Initialize the Flask-Fixtures mixin class
FixturesMixin.init_app(app, db)

# Make sure to inherit from the FixturesMixin class
class TestFoo(unittest.TestCase, FixturesMixin):

    # Specify the fixtures file you want to load
    fixtures = ['authors.json']

    # Your tests go here

    def test_authors(self):
        authors = Author.query.all()
        assert len(authors) == Author.query.count() == 1
        assert len(authors[0].books) == 3

    def test_books(self):
        books = Book.query.all()
        assert len(books) == Book.query.count() == 3
        gibson = Author.query.filter(Author.last_name=='Gibson').one()
        for book in books:
            assert book.author == gibson
