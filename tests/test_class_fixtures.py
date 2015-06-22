import unittest

from myapp import app
from myapp.models import db, Book, Author

from flask.ext.fixtures import FixturesMixin

# Configure the app with the testing configuration
app.config.from_object('myapp.config.TestConfig')

# Initialize the Flask-Fixtures mixin class
FixturesMixin.init_app(app, db)


class TestClassFixtures(unittest.TestCase, FixturesMixin):

    # Specify the fixtures file(s) you want to load
    class_fixtures = ['authors.json']

    # Your tests go here

    @classmethod
    def setUpClass(self):
        # Make sure that the user defined setUp method runs after the fixtures
        # setup function (i.e., the database should be setup already)
        assert Author.query.count() == 1
        assert Book.query.count() == 3

    @classmethod
    def tearDownClass(self):
        # This should run before the fixtures tear down function, so the
        # database should still contain all the fixtures data
        assert Author.query.count() == 3
        assert Book.query.count() == 3

    def test_one(self):
        print "Inside test_one"
        # Add another author on the fly
        author = Author()
        author.first_name = 'George'
        author.last_name = 'Orwell'
        self.db.session.add(author)
        self.db.session.commit()

    def test_two(self):
        print "Inside test_two"
        # Add another author on the fly
        author = Author()
        author.first_name = 'Aldous'
        author.last_name = 'Huxley'
        self.db.session.add(author)
        self.db.session.commit()

