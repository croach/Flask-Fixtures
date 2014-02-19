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


def setup(obj):
  # Setup the database
  print("setting up database...")
  obj.db.create_all()
  # TODO why do we call this?
  obj.db.session.rollback()

  # Load all of the fixtures
  fixtures_dirs = obj.app.config['FIXTURES_DIRS']
  for filename in obj.fixtures:
    for directory in fixtures_dirs:
      filepath = os.path.join(directory, filename)
      if os.path.exists(filepath):
        # TODO load the data into the database
        load_fixtures(obj.db, load_file(filepath))
        break
    else:
      # TODO should we raise an error here instead?
      print("Error loading %s" % filename, file=sys.stderr)


def teardown(obj):
  obj.db.session.expunge_all()
  obj.db.drop_all()


def load_file(filename):
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


def load_fixtures(db, fixtures):
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
  def __new__(meta, name, bases, attrs):
    if attrs.get('fixtures', None) is not None:
      parent_setup = attrs.pop('setUpClass', None)
      parent_teardown = attrs.pop('tearDownClass', None)
      attrs['setUpClass'] = classmethod(meta.fixtures_handler(setup, parent_setup))
      attrs['tearDownClass'] = classmethod(meta.fixtures_handler(teardown, parent_teardown))
      # attrs['setUp'] = meta.fixtures_handler(setup(fixtures), parent_setup)
      # attrs['tearDown'] = meta.fixtures_handler(teardown, parent_teardown)

    return super(MetaFixturesMixin, meta).__new__(meta, name, bases, attrs)


  @staticmethod
  def fixtures_handler(fn, parent_fn=None):
    parent_fn = (lambda obj: None) if parent_fn is None else parent_fn
    def handler(obj):
      parent_fn.__get__(obj)()
      fn(obj)
    return handler


class FixturesMixin(object):

  __metaclass__ = MetaFixturesMixin

  fixtures = None

  @classmethod
  def init_app(cls, app, db=None):
    default_fixtures_dir = os.path.join(app.root_path, 'fixtures')
    # app.config.setdefault('FIXTURES_DIRS', [default_fixtures_dir])
    fixtures_dirs = [default_fixtures_dir] + app.config.get('FIXTURES_DIRS', [])
    app.config['FIXTURES_DIRS'] = fixtures_dirs
    # app.config.setdefault("SQLALCHEMY_DATABASE_URI", 'sqlite://:memory:')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    # app.test = True
    # app.debug = True
    cls.app = app
    cls.db = db

