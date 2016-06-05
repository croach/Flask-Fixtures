"""
    test_fixtures
    ~~~~~~~~~~~~~

    A set of tests that check the default functionality of Flask-Fixtures.

    :copyright: (c) 2015 Christopher Roach <ask.croach@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""


from __future__ import absolute_import

import unittest

from myapp import app
from myapp.models import db, Book, Author

from flask.ext.fixtures import FixturesMixin

# Configure the app with the testing configuration
app.config.from_object('myapp.config.TestConfig')


class TestMyApp(unittest.TestCase, FixturesMixin):
    """A basic set of tests to make sure that fixtures works.
    """

    # Specify the fixtures file(s) you want to load
    fixtures = ['authors.json']

    # Specify the Flask app and database we want to use for this set of tests
    app = app
    db = db

    # Your tests go here

    def test_add_author(self):
        # Add another author on the fly
        author = Author()
        author.first_name = 'George'
        author.last_name = 'Orwell'
        self.db.session.add(author)
        self.db.session.commit()


# Make sure to inherit from the FixturesMixin class
class TestMyAppWithUserDefinedFunctions(unittest.TestCase, FixturesMixin):
    """Tests that functions like setUp and tearDown work
    """

    # Specify the fixtures file(s) you want to load
    fixtures = ['authors.json']

    # Specify the Flask app and database we want to use for this set of tests
    app = app
    db = db

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


class TestMyAppWithRequestContext(TestMyAppWithUserDefinedFunctions):
    """Tests that manually pushing a request context works.

    Just as with the app context test (see above), fixtures should work when
    the user manually pushes a request context onto the stack, e.g., when the
    developer uses the `test_request_context()` context manager.

    """

    # Make sure the app object is None, so this test will fail if we don't
    # have an app context on the stack
    app = None

    def setUp(self):
        self.ctx = app.test_request_context()
        self.ctx.push()
        super(TestMyAppWithRequestContext, self).setUp()

    def tearDown(self):
        super(TestMyAppWithRequestContext, self).tearDown()
        self.ctx.pop()


# Only run this test if we are using a version of Flask that supports app
# contexts (i.e., Flask >= 0.9)
if hasattr(app, 'app_context'):
    class TestMyAppWithAppContext(TestMyAppWithUserDefinedFunctions):
        """Tests that manually pushing a app context works.

        The normal way to specify a Flask application to test is to set it equal
        to the `app` class variable. However, this could also be done by creating
        an app context and pushing onto the stack as well. This test makes sure
        that everything works, even when this method is used.

        """

        # Make sure the app object is None, so this test will fail if we don't
        # have an app context on the stack
        app = None

        def setUp(self):
            self.ctx = app.app_context()
            self.ctx.push()
            super(TestMyAppWithAppContext, self).setUp()

        def tearDown(self):
            super(TestMyAppWithAppContext, self).tearDown()
            self.ctx.pop()
