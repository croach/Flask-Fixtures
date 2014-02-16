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



class Loader(object):

  def __init__(self, filenames):
    self.filenames = filenames

  def __call__(self, parent):
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


  def load_file(self, filename):
    """Returns list of fixtures from the given file.
    """
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


  def load_fixtures(self, db, fixtures):
    """Loads the given fixtures into the database.
    """
    for fixture in fixtures:

      if 'table' in fixture:
        table = fixture.get('table')


      elif 'model' in fixture:
        model = fixture.get('model')




# def load_data(db, fixtures):
#   """Loads the given fixtures into the database.
#   """
#   for fixture in fixtures:
#     if 'table' in fixture:

#     elif 'model' in fixture:
#       pass

# def load_fixtures(filename):
#   """Loads the fixtures found in the given file and returns the resultant dict.
#   """
#   name, extension = os.path.splitext(filename)
#   if extension.lower() in ('.yaml', '.yml'):
#     loader = yaml.load
#   elif extension.lower() in ('.json', '.js'):
#     loader = json.load
#   else:
#     # Try both supported formats
#     def loader(f):
#       try:
#         return yaml.load(f)
#       except Exception:
#         pass
#       try:
#         return json.load(f)
#       except Exception:
#         pass
#       raise Exception("Could not load fixture '%s': unsupported format")
#   with open(filename, 'r') as fin:
#     return loader(fin)


# def init_database(fixtures):
#   def _init_database(cls, *args, **kwargs):
#     fixtures_directory = cls.app.config['FIXTURES_DIRS']
#     for fixture in fixtures:
#       for directory in fixtures_directory:
#         filename = os.path.join(directory, fixture)
#         if os.path.exists(filename):
#           data = load_fixtures(filename)
#           # TODO load the data into the database
#           import ipdb; ipdb.set_trace()
#           load_data(data)
#           print(data)
#           break
#       else:
#         # TODO should we raise an error here instead?
#         print("Error loading %s" % fixture, file=sys.stderr)

#   return _init_database


class MetaFixturesMixin(type):
  def __new__(metaclass, name, bases, attrs):

    fixtures = attrs.pop('fixtures', None)
    if fixtures is not None:
      # attrs['setup_class'] = classmethod(init_database(fixtures))
      attrs['setup_class'] = classmethod(Loader(fixtures))

    return super(MetaFixturesMixin, metaclass).__new__(metaclass, name, bases, attrs)


class FixturesMixin(object):

  __metaclass__ = MetaFixturesMixin

  fixtures = None

  @classmethod
  def init_app(cls, app, db=None):
    default_fixtures_dir = os.path.join(app.root_path, 'fixtures')
    app.config.setdefault('FIXTURES_DIRS', [default_fixtures_dir])
    app.test = True
    cls.app = app
    cls.db = db

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


# def test_case_mixin_maker(app=None, db=None):
#   TestCaseMixin.app = app
#   TestCaseMixin.db = db


# def init_fixtures_mixin(app, db=None):
#   if app is not None:
#     default_fixtures_dir = os.path.join(app.root_path, 'fixtures')
#     app.config.setdefault('FIXTURES_DIRS', [default_fixtures_dir])
#     # TestCaseMixin.app = app
#     app.test = True
#   FixturesMixin.app = app
#   FixturesMixin.db = db
#   # .__dict__.update({
#   #   'app': app,
#   #   'db': db
#   # })
#   return FixturesMixin


# class Fixtures(object):

#   def __init__(self, app=None, db=None):
#     self.TestCaseMixin = type('TestCaseMixin', (object,), {
#         '__metaclass__': MetaTestCaseMixin,
#         'fixtures': None,
#         'app': app,
#         'db': db
#       })
#     self.init_app(app, db)
#     # self.app = app
#     # self.db = db
#     # self.TestCaseMixin = TestCaseMixin
#     # if app is not None:
#     #   self.init_app(app)

#   def init_app(self, app, db=None):
#     default_fixtures_dir = os.path.join(app.root_path, 'fixtures')
#     app.config.setdefault('FIXTURES_DIRS', [default_fixtures_dir])
#     # TestCaseMixin.app = app
#     app.test = True

