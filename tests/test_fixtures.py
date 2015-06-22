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

    # Specify the fixtures file(s) you want to load
    fixtures = ['authors.json']

    # Your tests go here

    def setUp(self):
        # Make sure that the user defined setUp method runs after the fixtures
        # setup function (i.e., the database should be setup already)
        assert Author.query.count() == 1
        assert Book.query.count() == 3

        # Add another author on the fly
        author = Author()
        author.first_name = 'George'
        author.last_name = 'Orwell'
        self.db.session.add(author)
        self.db.session.commit()

    def tearDown(self):
        # This should run before the fixtures tear down function, so the
        # database should still contain all the fixtures data
        assert Author.query.count() == 2
        assert Book.query.count() == 3

    def test_authors(self):
        authors = Author.query.all()
        assert len(authors) == Author.query.count() == 2
        assert len(authors[0].books) == 3

    def test_books(self):
        books = Book.query.all()
        assert len(books) == Book.query.count() == 3
        gibson = Author.query.filter(Author.last_name=='Gibson').one()
        for book in books:
            assert book.author == gibson


class TestWithoutUserDefinedFunctions(unittest.TestCase, FixturesMixin):
    """Tests everything is working without user defined setup/teardown functions
    """

    # Specify the fixtures file(s) you want to load
    fixtures = ['authors.json']

    # Your tests go here

    def test_add_author(self):
        # Add another author on the fly
        author = Author()
        author.first_name = 'George'
        author.last_name = 'Orwell'
        self.db.session.add(author)
        self.db.session.commit()
