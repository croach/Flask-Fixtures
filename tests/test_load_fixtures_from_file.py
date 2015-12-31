from __future__ import absolute_import

import unittest

from myapp import app
from myapp.models import db, Book, Author

from flask.ext.fixtures import load_fixtures_from_file

# Configure the app with the testing configuration
app.config.from_object('myapp.config.TestConfig')

class TestLoadFixturesFromFile(unittest.TestCase):
    def setUp(self):
        # Setup the database
        db.create_all()
        # Rollback any lingering transactions
        db.session.rollback()

    def tearDown(self):
        db.session.expunge_all()
        db.drop_all()

    def test_load_fixtures_file_json(self):
        load_fixtures_from_file(db, 'authors.json', app.config['FIXTURES_DIRS'])
        assert Author.query.count() == 1
        assert Book.query.count() == 3

    def test_load_fixtures_file_json_abs(self):
        load_fixtures_from_file(db, 'myapp/fixtures/authors.json')
        assert Author.query.count() == 1
        assert Book.query.count() == 3

    def test_load_fixtures_file_yaml(self):
        load_fixtures_from_file(db, 'authors.yaml', app.config['FIXTURES_DIRS'])
        assert Author.query.count() == 1
        assert Book.query.count() == 3
