from __future__ import print_function

import inspect
import os
import sys

from flask import current_app
from sqlalchemy import Table

try:
  import simplejson as json
except ImportError:
  import json

try:
  import yaml
  YAML_INSTALLED = True
except ImportError:
  YAML_INSTALLED = False


class Loader(object):
  """A callable object that handles the loading of fixtures into the database.
  """

  def __init__(self, filenames):
    self.filenames = filenames


  def __call__(self, parent):
    if not hasattr(self, 'loader'):
      self.loader = self.create_loader(parent)
    try:
      self.loader.next()
    except StopIteration:
      del self.loader


  def create_loader(self, parent):
    """Creates a function that handles setup, loading, and teardown of the db.

    Returns a generator function that, when called the first time, sets up the
    database (i.e., creates the tables, etc.) and loads all fixtures into it,
    and, when called the second time, tears the database down.
    """
    def _loader():
      # Setup the database and load all of the fixtures
      self.setup_db(parent.db)
      fixtures_dirs = parent.app.config['FIXTURES_DIRS']
      for filename in self.filenames:
        for directory in fixtures_dirs:
          filepath = os.path.join(directory, filename)
          if os.path.exists(filepath):
            fixtures = self.load_file(filepath)
            # TODO load the data into the database
            self.load_fixtures(parent.db, fixtures)
            break
        else:
          # TODO should we raise an error here instead?
          print("Error loading %s" % filename, file=sys.stderr)

      # Pause for the test(s) to be run
      (yield)

      # Tear the database down after all tests have finished
      self.teardown_db(parent.db)
    return _loader()


  def setup_db(self, db):
    print("setting up database...")
    db.create_all()
    # TODO why do we call this?
    db.session.rollback()


  def teardown_db(self, db):
    print("tearing down database...")
    db.session.expunge_all()
    db.drop_all()


  def load_file(self, filename):
    """Returns list of fixtures from the given file.
    """
    name, extension = os.path.splitext(filename)
    if extension.lower() in ('.yaml', '.yml'):
      if not YAML_INSTALLED:
        raise Exception("Could not load fixture '%s'; PyYAML must first be installed")
      loader = yaml.load
    elif extension.lower() in ('.json', '.js'):
      loader = json.load
    else:
      # Try both supported formats
      def loader(f):
        try:
          return yaml.load(f)
        except Exception:
          pass
        try:
          return json.load(f)
        except Exception:
          pass
        raise Exception("Could not load fixture '%s'; unsupported format")
    with open(filename, 'r') as fin:
      return loader(fin)


  def load_fixtures(self, db, fixtures):
    """Loads the given fixtures into the database.
    """
    conn = db.engine.connect()
    metadata = db.metadata

    for fixture in fixtures:

      if 'table' in fixture:
        table = Table(fixture.get('table'), metadata)


      elif 'model' in fixture:
        model = fixture.get('model')


class MetaFixturesMixin(type):
  def __new__(metaclass, name, bases, attrs):
    fixtures = attrs.pop('fixtures', None)
    if fixtures is not None:
      attrs['setup_class'] = attrs['teardown_class'] = classmethod(Loader(fixtures))

    return super(MetaFixturesMixin, metaclass).__new__(metaclass, name, bases, attrs)


class FixturesMixin(object):

  __metaclass__ = MetaFixturesMixin

  fixtures = None

  @classmethod
  def init_app(cls, app, db=None):
    default_fixtures_dir = os.path.join(app.root_path, 'fixtures')
    app.config.setdefault('FIXTURES_DIRS', [default_fixtures_dir])
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", 'sqlite://')
    # app.test = True
    # app.debug = True
    cls.app = app
    cls.db = db

