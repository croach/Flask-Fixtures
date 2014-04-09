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

import abc
import functools
import glob
import importlib
import inspect
import os
import sys

from sqlalchemy import Table

from . import loaders

try:
  import simplejson as json
except ImportError:
  import json


__version__ = '0.3.1'


DEFAULT_CLASS_SETUP_NAME = 'setUpClass'
DEFAULT_CLASS_TEARDOWN_NAME = 'tearDownClass'
CLASS_SETUP_NAMES = ('setup_class', 'setup_all', 'setupClass', 'setupAll',
                     'setUpClass', 'setUpAll')
CLASS_TEARDOWN_NAMES = ('teardown_class', 'teardown_all', 'teardownClass',
                     'teardownAll', 'tearDownClass', 'tearDownAll')
TEST_SETUP_NAMES = ('setUp',)
TEST_TEARDOWN_NAMES = ('tearDown',)


class Fixtures(object):
  def __init__(self, app, db):
    self.init_app(app, db)

  def init_app(self, app, db):
    self.app = app
    self.db = db

  @property
  def fixtures_dirs(self):
    default_fixtures_dir = os.path.join(self.app.root_path, 'fixtures')

    # All relative paths should be relative to the app's root directory.
    fixtures_dirs = [default_fixtures_dir]
    for directory in self.app.config.get('FIXTURES_DIRS', []):
      if not os.path.isabs(directory):
        directory = os.path.abspath(os.path.join(self.app.root_path, directory))
      fixtures_dirs.append(directory)

    return fixtures_dirs

  def setup(self, fixtures):
    print("setting up fixtures...")
    # Setup the database
    self.db.create_all()
    # TODO why do we call this?
    self.db.session.rollback()

    # Load all of the fixtures
    for filename in fixtures:
      # If the filename is an absolute filepath, just go ahead and load it,
      # otherwise, look through each of the directories in the FIXTURES_DIRS
      # list until you find a file matching the current filename. Raise an
      # exception if the file can't be found.
      if os.path.isabs(filename):
        filepath = filename
      else:
        for directory in self.fixtures_dirs:
          filepath = os.path.join(directory, filename)
          if os.path.exists(filepath):
            break
        else:
          raise IOError("Error loading fixture, '%s' could not be found" % filename)

      # Load the current fixture into the database
      self.load_fixtures(loaders.load(filepath))

  def teardown(self):
    print("tearing down fixtures...")
    self.db.session.expunge_all()
    self.db.drop_all()

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

  def find_fixtures(self, obj, fixtures):
    """Returns the filepaths of the fixtures for the given object.

    This function attempts to find fixtures files in the same directory as the
    given object's module.
    """
    # Search in the same directory as the test script for a file with the same
    # name, and a supported format's file extension.
    test_file = sys.modules[obj.__module__].__file__
    filename, ext = os.path.splitext(test_file)
    candidate_files = [f for f in glob.glob("%s.*" % filename) if not f.endswith(ext)]
    fixtures = [f for f in candidate_files if os.path.splitext(f)[1] in loaders.extensions()]

    # if fixtures are still empty, raise an exception
    if len(fixtures) == 0:
      raise Exception("Could not find fixtures for '%s'" % test_file)

    return fixtures

  def wrap_method(self, method, fixtures):
    """Wraps a method in a set of fixtures setup/teardown functions.
    """
    if len(fixtures) == 0:
      fixtures = self.find_fixtures(method, fixtures)

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
    def wrap_method(cls, fixtures_fn, names, default_name):
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
        setattr(cls, default_name, classmethod(wrapper))

    # if fixtures aren't empty, just return the ones that were passed in
    if len(fixtures) == 0:
      fixtures = self.find_fixtures(cls, fixtures)

    wrap_method(cls, lambda: self.setup(fixtures), CLASS_SETUP_NAMES, DEFAULT_CLASS_SETUP_NAME)
    wrap_method(cls, lambda: self.teardown(), CLASS_TEARDOWN_NAMES, DEFAULT_CLASS_TEARDOWN_NAME)

    return cls

  def __call__(self, *fixtures):
    # The object being decorated/wrapped
    wrapped_obj = None

    # If the decorator was called without parentheses, the fixtures parameter
    # will be a list containing the object being decorated rather than a list
    # of fixtures to install. In that case, we set the fixtures variable to an
    # empty list and the wrapped_obj variable to the object being decorated so
    # we can call the decorator on it later.
    if len(fixtures) == 1 and not isinstance(fixtures[0], basestring):
      wrapped_obj = fixtures[0]
      fixtures = ()

    # Create the decorator function
    def decorator(obj):
      if inspect.isfunction(obj):
        return self.wrap_method(obj, fixtures)
      elif inspect.isclass(obj):
        return self.wrap_class(obj, fixtures)
      else:
        raise TypeError("received an object of type '%s' expected 'function' or 'classobj'" % type(obj))

    # If we were passed the object to decorate, go ahead and call the
    # decorator on it and pass back the result, otherwise, return the
    # decorator
    if wrapped_obj is not None:
      return decorator(wrapped_obj)
    else:
      return decorator
