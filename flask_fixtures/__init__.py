"""
    flask_fixtures
    ~~~~~~~~~~~~~~~~~~

    Flask-Fixtures is a `Flask <http://flask.pocoo.org>`_ extension that aids
    in the creation of fixtures data from serialized data files. It is
    compatible with the `SQLAlchemy <http://sqlalchemy.org>`_ library.

    :copyright: (c) 2015 Christopher Roach <ask.croach@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import absolute_import

import logging
import os

from sqlalchemy import Table

from . import loaders
from .utils import can_persist_fixtures
import six
import importlib

from flask import current_app
from flask import _request_ctx_stack
try:
    from flask import _app_ctx_stack
except ImportError:
    _app_ctx_stack = None

try:
    import simplejson as json
except ImportError:
    import json

__version__ = '0.3.8'


# Configure the root logger for the library
logger_format_string = '[%(levelname)s] %(message)s in File "%(pathname)s", line %(lineno)d, in %(funcName)s'
logging.basicConfig(format=logger_format_string, level=logging.INFO)
log = logging.getLogger(__name__)


CLASS_SETUP_NAMES = ('setUpClass', 'setup_class', 'setup_all', 'setupClass', 'setupAll', 'setUpAll')
CLASS_TEARDOWN_NAMES = ('tearDownClass', 'teardown_class', 'teardown_all', 'teardownClass', 'teardownAll', 'tearDownAll')
TEST_SETUP_NAMES = ('setUp',)
TEST_TEARDOWN_NAMES = ('tearDown',)

def push_ctx(app=None):
    """Creates new test context(s) for the given app

    If the app is not None, it overrides any existing app and/or request
    context. In other words, we will use the app that was passed in to create
    a new test request context on the top of the stack. If, however, nothing
    was passed in, we will assume that another app and/or  request context is
    already in place and use that to run the test suite. If no app or request
    context can be found, an AssertionError is emitted to let the user know
    that they must somehow specify an application for testing.

    """
    if app is not None:
        ctx = app.test_request_context()
        ctx.fixtures_request_context = True
        ctx.push()
        if _app_ctx_stack is not None:
            _app_ctx_stack.top.fixtures_app_context = True

    # Make sure that we have an application in the current context
    if (_app_ctx_stack is None or _app_ctx_stack.top is None) and _request_ctx_stack.top is None:
        raise AssertionError('A Flask application must be specified for Fixtures to work.')


def pop_ctx():
    """Removes the test context(s) from the current stack(s)
    """
    if getattr(_request_ctx_stack.top, 'fixtures_request_context', False):
        _request_ctx_stack.pop()
    if _app_ctx_stack is not None and getattr(_app_ctx_stack.top, 'fixtures_app_context', False):
        _app_ctx_stack.pop()


def setup(obj):
    log.info('setting up fixtures...')

    # Push a request and/or app context onto the stack
    push_ctx(getattr(obj, 'app'))

    # Setup the database
    obj.db.create_all()
    # Rollback any lingering transactions
    obj.db.session.rollback()


    # Construct a list of paths within which fixtures may reside
    default_fixtures_dir = os.path.join(current_app.root_path, 'fixtures')

    # All relative paths should be relative to the app's root directory.
    fixtures_dirs = [default_fixtures_dir]
    for directory in current_app.config.get('FIXTURES_DIRS', []):
        if not os.path.isabs(directory):
            directory = os.path.abspath(os.path.join(current_app.root_path, directory))
        fixtures_dirs.append(directory)

    # Load all of the fixtures
    for filename in obj.fixtures:
        load_fixtures_from_file(obj.db, filename, fixtures_dirs)


def teardown(obj):
    log.info('tearing down fixtures...')
    obj.db.session.expunge_all()
    obj.db.drop_all()
    pop_ctx()


def load_fixtures_from_file(db, fixture_filename, fixtures_dirs=[]):
    fixtures_dirs = set(fixtures_dirs)
    fixtures_dirs.add('.')
    for directory in fixtures_dirs:
        filepath = os.path.join(directory, fixture_filename)
        if os.path.exists(filepath):
            # TODO load the data into the database
            load_fixtures(db, loaders.load(filepath))
            break
    else:
        raise IOError("Error loading '{0}'. File could not be found".format(fixture_filename))


def load_fixtures(db, fixtures):
    """Loads the given fixtures into the database.
    """
    conn = db.engine.connect()
    metadata = db.metadata

    for fixture in fixtures:
        if 'model' in fixture:
            module_name, class_name = fixture['model'].rsplit('.', 1)
            module = importlib.import_module(module_name)
            model = getattr(module, class_name)
            for fields in fixture['records']:
                obj = model(**fields)
                db.session.add(obj)
            db.session.commit()
        elif 'table' in fixture:
            table = Table(fixture['table'], metadata)
            conn.execute(table.insert(), fixture['records'])
        else:
            raise ValueError("Fixture missing a 'model' or 'table' field: {0}".format(json.dumps(fixture)))


class MetaFixturesMixin(type):
    def __new__(meta, name, bases, attrs):

        fixtures = attrs.get('fixtures', [])

        # Should we persist fixtures across tests, i.e., should we use the
        # setUpClass and tearDownClass methods instead of setUp and tearDown?
        persist_fixtures = attrs.get('persist_fixtures', False) and can_persist_fixtures()

        # We only need to do something if there's a set of fixtures,
        # otherwise, do nothing. The main reason this is here is because this
        # method is called when the FixturesMixin class is created and we
        # don't want to do any test setup on that class.
        if fixtures:
            if not persist_fixtures:
                child_setup_fn = meta.get_child_fn(attrs, TEST_SETUP_NAMES, bases)
                child_teardown_fn = meta.get_child_fn(attrs, TEST_TEARDOWN_NAMES, bases)
                attrs[child_setup_fn.__name__] = meta.setup_handler(setup, child_setup_fn)
                attrs[child_teardown_fn.__name__] = meta.teardown_handler(teardown, child_teardown_fn)
            else:
                child_setup_fn = meta.get_child_fn(attrs, CLASS_SETUP_NAMES, bases)
                child_teardown_fn = meta.get_child_fn(attrs, CLASS_TEARDOWN_NAMES, bases)
                attrs[child_setup_fn.__name__] = classmethod(meta.setup_handler(setup, child_setup_fn))
                attrs[child_teardown_fn.__name__] = classmethod(meta.teardown_handler(teardown, child_teardown_fn))

        return super(MetaFixturesMixin, meta).__new__(meta, name, bases, attrs)

    @staticmethod
    def setup_handler(setup_fixtures_fn, setup_fn):
        """Returns a function that adds fixtures handling to the setup method.

        Makes sure that fixtures are setup before calling the given setup method.
        """
        def handler(obj):
            setup_fixtures_fn(obj)
            setup_fn(obj)
        return handler

    @staticmethod
    def teardown_handler(teardown_fixtures_fn, teardown_fn):
        """Returns a function that adds fixtures handling to the teardown method.

        Calls the given teardown method first before calling the fixtures teardown.
        """
        def handler(obj):
            teardown_fn(obj)
            teardown_fixtures_fn(obj)
        return handler

    @staticmethod
    def get_child_fn(attrs, names, bases):
        """Returns a function from the child class that matches one of the names.

        Searches the child class's set of methods (i.e., the attrs dict) for all
        the functions matching the given list of names. If more than one is found,
        an exception is raised, if one is found, it is returned, and if none are
        found, a function that calls the default method on each parent class is
        returned.

        """
        def call_method(obj, method):
            """Calls a method as either a class method or an instance method.
            """
            # The __get__ method takes an instance and an owner which changes
            # depending on the calling object. If the calling object is a class,
            # the instance is None and the owner will be the object itself. If the
            # calling object is an instance, the instance will be the calling object
            # and the owner will be its class. For more info on the __get__ method,
            # see http://docs.python.org/2/reference/datamodel.html#object.__get__.
            if isinstance(obj, type):
                instance = None
                owner = obj
            else:
                instance = obj
                owner = obj.__class__
            method.__get__(instance, owner)()

        # Create a default function that calls the default method on each parent
        default_name = names[0]
        def default_fn(obj):
            for cls in bases:
                if hasattr(cls, default_name):
                    call_method(obj, getattr(cls, default_name))
        default_fn.__name__ = default_name

        # Get all of the functions in the child class that match the list of names
        fns = [(name, attrs[name]) for name in names if name in attrs]

        # Raise an error if more than one setup/teardown method is found
        if len(fns) > 1:
            raise RuntimeError("Cannot have more than one setup or teardown method per context (class or test).")
        # If one setup/teardown function was found, return it
        elif len(fns) == 1:
            name, fn = fns[0]
            def child_fn(obj):
                call_method(obj, fn)
            child_fn.__name__ = name
            return child_fn
        # Otherwise, return the default function
        else:
            return default_fn


class FixturesMixin(six.with_metaclass(MetaFixturesMixin, object)):

    fixtures = None
    app = None
    db = None
