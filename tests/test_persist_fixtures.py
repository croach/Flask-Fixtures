import datetime
import inspect
import os
import sys
import unittest

from myapp import app
from myapp.models import db, Book, Author

from flask.ext.fixtures import FixturesMixin

# Configure the app with the testing configuration
app.config.from_object('myapp.config.TestConfig')

# Initialize the Flask-Fixtures mixin class
FixturesMixin.init_app(app, db)


def can_run_tests():
    """Checks if the tests in this file can be ran or not.

    The setUpClass and tearDownClass methods were added to unittest.TestCase
    in python 2.7. So, we can only run the tests in this file if we are using
    python 2.7. However, the nose and py.test libraries add support for these
    methods regardless of what version of python we are running, so if we are
    running with either of those libraries, go ahead and execute the tests as
    well.

    """
    # If we're running python 2.7 or greater, we're fine
    if sys.hexversion >= 0x02070000:
        return True

    # Otherwise, nose and py.test support the setUpClass and tearDownClass
    # methods, so if we're using either of those, go ahead and run the tests
    filename = inspect.stack()[-1][1]
    executable = os.path.split(filename)[1]
    return executable in ('py.test', 'nosetests')


# The setUpClass and tearDownClass methods were added to unittest.TestCase in
# python 2.7, so if we're running a version of python below that this test
# will fail. So, make sure we only run the test with python 2.7 or greater.
if can_run_tests():

    class TestPersistFixtures(unittest.TestCase, FixturesMixin):

        # Specify the fixtures file(s) you want to load
        fixtures = ['authors.json']
        persist_fixtures = True

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

