from __future__ import absolute_import

import os
import unittest

from myapp import app
from myapp.models import db, Book, Author

from flask_fixtures import load_fixtures_from_file, push_ctx, pop_ctx

# Configure the app with the testing configuration
app.config.from_object('myapp.config.TestConfig')
fixtures_dirs = [os.path.join(app.root_path, 'fixtures')]

class TestLoadFixturesFromFile(unittest.TestCase):
    def setUp(self):
        push_ctx(app)
        # Setup the database
        db.create_all()
        # Rollback any lingering transactions
        db.session.rollback()

    def tearDown(self):
        db.session.expunge_all()
        db.drop_all()
        pop_ctx()

    def test_load_fixtures_file_json(self):
        load_fixtures_from_file(db, 'authors.json', fixtures_dirs)
        assert Author.query.count() == 1
        assert Book.query.count() == 3

    def test_load_fixtures_file_json_abs(self):
        load_fixtures_from_file(db, 'myapp/fixtures/authors.json')
        assert Author.query.count() == 1
        assert Book.query.count() == 3

    def test_load_fixtures_file_yaml(self):
        load_fixtures_from_file(db, 'authors.yaml', fixtures_dirs)
        assert Author.query.count() == 1
        assert Book.query.count() == 3
