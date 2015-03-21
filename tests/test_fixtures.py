import unittest

from myapp import app
from myapp.models import db, Book, Author

from flask.ext.fixtures import FixturesMixin

app.config.from_object('myapp.config.TestConfig')
FixturesMixin.init_app(app, db)

class TestFoo(unittest.TestCase, FixturesMixin):
    fixtures = ['authors.json']

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

