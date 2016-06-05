"""
    test_persist_fixtures
    ~~~~~~~~~~~~~~~~~~~~~

    A set of tests for checking the `persist_fixtures` feature of Flask-
    Fixtures. The default behavior for Fixtures is to completely destroy and
    rebuild the database from scratch for each individual test. This is
    typically preferred, since it limits the number of false negatives by
    making sure that each test runs independently, and is therefore not
    affected by previous tests. However, if there is a need to run a set of
    tests without a complete refresh of the test fixtures (e.g., for
    performance reasons), the `persist_fixtures` flag can be set to `True` to
    do so. This set of tests makes sure that the `persist_fixtures` flag works
    as expected.

    :copyright: (c) 2015 Christopher Roach <ask.croach@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""


from __future__ import absolute_import
from __future__ import print_function
import datetime
import inspect
import os
import sys
import unittest

from myapp import app
from myapp.models import db, Book, Author

from flask.ext.fixtures import FixturesMixin
from flask.ext.fixtures.utils import can_persist_fixtures

# Configure the app with the testing configuration
app.config.from_object('myapp.config.TestConfig')


# The setUpClass and tearDownClass methods were added to unittest.TestCase in
# python 2.7, so if we're running a version of python below that this test
# will fail. So, make sure we only run the test with python 2.7 or greater.
if can_persist_fixtures():

    class TestPersistFixtures(unittest.TestCase, FixturesMixin):

        # Specify the fixtures file(s) you want to load
        fixtures = ['authors.json']
        persist_fixtures = True

        # Specify the Flask app and database we want to use for this set of tests
        app = app
        db = db

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
            print("Inside test_one")
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
            print("Inside test_two")
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

