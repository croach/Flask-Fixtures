"""
(c) 2014 LinkedIn Corp.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
   limitations under the License.
"""

from __future__ import print_function

import functools
import importlib
import inspect
import os
import sys

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


CLASS_SETUP_NAMES = ('setUpClass', 'setup_class', 'setup_all', 'setupClass', 'setupAll', 'setUpAll')
CLASS_TEARDOWN_NAMES = ('tearDownClass', 'teardown_class', 'teardown_all', 'teardownClass', 'teardownAll', 'tearDownAll')
TEST_SETUP_NAMES = ('setUp',)
TEST_TEARDOWN_NAMES = ('tearDown',)


class Fixtures(object):
  def __init__(self, app, db):
    self.init_app(app, db)

  def init_app(self, app, db):
    default_fixtures_dir = os.path.join(app.root_path, 'fixtures')

    # All relative paths should be relative to the app's root directory.
    fixtures_dirs = [default_fixtures_dir]
    for directory in app.config.get('FIXTURES_DIRS', []):
      if not os.path.isabs(directory):
        directory = os.path.abspath(os.path.join(app.root_path, directory))
      fixtures_dirs.append(directory)
    app.config['FIXTURES_DIRS'] = fixtures_dirs
    self.app = app
    self.db = db

  def setup(self, fixtures):
    print("setting up fixtures...")
    # Setup the database
    self.db.create_all()
    # TODO why do we call this?
    self.db.session.rollback()

    # Load all of the fixtures
    fixtures_dirs = self.app.config['FIXTURES_DIRS']
    for filename in fixtures:
      for directory in fixtures_dirs:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
          # TODO load the data into the database
          self.load_fixtures(self.load_file(filepath))
          break
      else:
        # TODO should we raise an error here instead?
        print("Error loading '%s'. File could not be found." % filename, file=sys.stderr)

  def teardown(self):
    print("tearing down fixtures...")
    self.db.session.expunge_all()
    self.db.drop_all()

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

  def load_fixtures(self, fixtures):
    """Loads the given fixtures into the database.
    """
    conn = self.db.engine.connect()
    metadata = self.db.metadata

    for fixture in fixtures:
      if 'model' in fixture:
        module_name, class_name = fixture['model'].rsplit('.', 1)
        module = importlib.import_module(module_name)
        model = getattr(module, class_name)
        for fields in fixture['records']:
          obj = model(**fields)
          self.db.session.add(obj)
        self.db.session.commit()
      elif 'table' in fixture:
        table = Table(fixture['table'], metadata)
        conn.execute(table.insert(), fixture['records'])
      else:
        raise ValueError("Fixture missing a 'model' or 'table' field: %s" % json.dumps(fixture))

  def wrap_method(self, method, fixtures):
    """Wraps a method in a set of fixtures setup/teardown functions.
    """
    def wrapper(*args, **kwargs):
      self.setup(fixtures)
      try:
        method(*args, **kwargs)
      finally:
        self.teardown()
    functools.update_wrapper(wrapper, method)
    return wrapper

  def wrap_class(self, cls, fixtures):
    """Adds fixtures setup/teardown methods at the class level.

    This decorator piggybacks on the setUpClass, tearDownClass methods that
    the unittest/unittest2/nose packages call upon class creation and after
    all tests in the class have finished running.

    """
    def wrap_method(cls, fixtures_fn, names):
      methods = filter(None, [getattr(cls, name, None) for name in names])
      if len(methods) > 1:
        raise RuntimeError("Cannot have more than one setup/teardown method, found %s" %
          ', '.join(fn.__name__ for fn in methods))
      elif len(methods) == 1:
        wrapped_method = methods[0]
        def wrapper(cls, *args, **kwargs):
          fixtures_fn()
          wrapped_method(*args, **kwargs)
        functools.update_wrapper(wrapper, wrapped_method)
        setattr(cls, wrapper.__name__, classmethod(wrapper))
      else:
        def wrapper(cls, *args, **kwargs):
          fixtures_fn()
          setattr(cls, 'setup_class', classmethod(wrapper))

    wrap_method(cls, lambda: self.setup(fixtures), CLASS_SETUP_NAMES)
    wrap_method(cls, lambda: self.teardown(), CLASS_TEARDOWN_NAMES)

    return cls

  def __call__(self, *fixtures):
    def decorator(obj):
      if inspect.isfunction(obj):
        return self.wrap_method(obj, fixtures)
      elif inspect.isclass(obj):
        return self.wrap_class(obj, fixtures)
      else:
        raise TypeError("received an object of type '%s' expected 'function' or 'classobj'" % type(obj))
    return decorator
