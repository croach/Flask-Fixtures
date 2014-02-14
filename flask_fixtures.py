from __future__ import print_function

import inspect
import os
import sys

from flask import current_app

try:
  import simplejson as json
except ImportError:
  import json

try:
  import yaml
  YAML_INSTALLED = True
except ImportError:
  YAML_INSTALLED = False


def load_fixtures(filename):
  name, extension = os.path.splitext(filename)
  if extension.lower() in ('.yaml', '.yml'):
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
      raise Exception("Could not load fixture '%s': unsupported format")
  with open(filename, 'r') as fin:
    return loader(fin)


def init_database(fixtures):
  def _init_database(cls, *args, **kwargs):
    fixtures_directory = cls.app.config['FIXTURES_DIRS']
    for fixture in fixtures:
      for directory in fixtures_directory:
        filename = os.path.join(directory, fixture)
        if os.path.exists(filename):
          data = load_fixtures(filename)
          # TODO load the data into the database
          print(data)
          break
      else:
        # TODO should we raise an error here instead?
        print("Error loading %s" % fixture, file=sys.stderr)

  return _init_database


class MetaTestCaseMixin(type):
  def __new__(cls, name, bases, attrs):
    fixtures = attrs.pop('fixtures', None)
    if fixtures is not None:
      attrs['setup_class'] = classmethod(init_database(fixtures))

    return super(MetaTestCaseMixin, cls).__new__(cls, name, bases, attrs)

class TestCaseMixin(object):

  __metaclass__ = MetaTestCaseMixin

  fixtures = None

  # @classmethod
  # def setUpClass(cls):
  #     'called once, before any tests'
  #     print 'class %s' % cls.__name__

  # @classmethod
  # def tearDownClass(cls):
  #     'called once, after all tests, if setUpClass successful'
  #     print 'class %s' % cls.__name__

  # def setUp(self):
  #     'called multiple times, before every test method'
  #     self.logPoint()

  # def tearDown(self):
  #     'called multiple times, after every test method'
  #     self.logPoint()


  # def logPoint(self):
  #     'utility method to trace control flow'
  #     callingFunction = inspect.stack()[1][3]
  #     print('in %s()' % (callingFunction))


class Fixtures(object):

  def __init__(self, app=None):
    self.app = app
    self.TestCaseMixin = TestCaseMixin
    if app is not None:
      self.init_app(app)

  def init_app(self, app):
    default_fixtures_dir = os.path.join(app.root_path, 'fixtures')
    app.config.setdefault('FIXTURES_DIRS', [default_fixtures_dir])
    TestCaseMixin.app = app
    app.test = True

