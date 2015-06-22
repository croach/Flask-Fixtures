import datetime
import sys
import unittest

from myapp import app
from myapp.models import db, Book, Author

from flask.ext.fixtures import FixturesMixin

# Configure the app with the testing configuration
app.config.from_object('myapp.config.TestConfig')

# Initialize the Flask-Fixtures mixin class
FixturesMixin.init_app(app, db)


# The setUpClass and tearDownClass methods were added to unittest.TestCase in
# python 2.7, so if we're running a version of python below that this test
# will fail. So, make sure we only run the test with python 2.7 or greater.
if sys.hexversion >= 0x02070000:

    class TestClassFixtures(unittest.TestCase, FixturesMixin):

        # Specify the fixtures file(s) you want to load
        class_fixtures = ['authors.json']

        @classmethod
        def setUpClass(self):
            # Make sure we start out with 1 author and 3 books
            assert Author.query.count() == 1
            assert Book.query.count() == 3

        @classmethod
        def tearDownClass(self):
            # Since we never tore down the DB in between tests, we should have 3
            # authors and 5 books now (the initial fixtures plus the records the
            # tests added).
            assert Author.query.count() == 3
            assert Book.query.count() == 5

        def test_one(self):
            print "Inside test_one"
            # Add another author on the fly
            author = Author()
            author.first_name = 'George'
            author.last_name = 'Orwell'
            self.db.session.add(author)

            # Add another book for the new author
            book = Book()
            book.title = "1984"
            book.published_date = datetime.datetime(1949, 6, 8)
            self.db.session.add(book)

            self.db.session.commit()

        def test_two(self):
            print "Inside test_two"
            # Add another author on the fly
            author = Author()
            author.first_name = 'Aldous'
            author.last_name = 'Huxley'
            self.db.session.add(author)

            # Add another book for the new author
            book = Book()
            book.title = "Brave New World"
            book.published_date = datetime.datetime(1932, 5, 12)
            self.db.session.add(book)

            self.db.session.commit()

