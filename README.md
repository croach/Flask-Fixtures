# Flask-Fixtures

A simple library that allows you to add database fixtures for your unit tests
using nothing but JSON or YAML.

## Installation

To install the library from source simply download the source code, or check
it out if you have git installed on your system. Then just run the install
command.

```
cd /path/to/flask-fixtures
python setup.py install
```

## Setup

To setup the library, you simply need to tell Flask-Fixtures where it can find
the fixtures files for your tests. Fixtures can reside anywhere on the file
system, but by default, Flask-Fixtures looks for these files in a directory
called `fixtures` in your app's root directory. To add more directories to the
list to be searched, just add an attribute called `FIXTURES_DIRS` to your app's
config object. This attribute should be a list of strings, each one being a path
to a fixtures directory. Absolute paths are added as is, but reltative paths
will be relative to your app's root directory.

Once you have configured the extension, you can begin adding fixtures for your
tests.

## Adding Fixtures

To add a set of fixtures, you simply add any number of JSON or YAML files
describing the individual fixtures to be added to your test database into one
of the directories you specified in the `FIXTURES_DIRS` attribute, or into the
default fixtures directory. As an example, we'll assume we have the following
classes in our code base.

```python
# myapp/__init__.py

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship('Author', backref='books')
```

And we'll also add the following configuration file as well.

```python
# myapp/config/__init__.py

class TestConfig(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    testing = True
    debug = True
    FIXTURES_DIRS = ['test/fixtures']
```

Given the classes above, if we wanted to mock up some data for our database, we
could do so in a single file, or we could even split our fixtures into multiple
files. For this simple example, we'll go with one file that we'll call
`authors.json`.

A fixtures file contains a list of objects. Each object contains a key called
`records` that  holds another list of objects each representing either a row in
a table, or an instance of a model. If you wish to work with tables, you'll need
to specify the name of the table with the `table` key. If you'd prefer to work
with models, specify the fully-qualified class name of the model using the
`model` key. Once you've specified the table or model you want to work with,
you'll need to specify the data associated with each table row or model
instance. Each object in the `records` list will hold the data for a single row
or model.

```json
[
    {
        "table": "author",
        "records": [{
            "id": 1,
            "first_name": "William",
            "last_name": "Gibson",
        }]
    },
    {
        "model": "myapp.models.Book",
        "records": [{
            "title": "Neuromancer",
            "author_id": 1
        },
        {
            "title": "Count Zero",
            "author_id": 1
        },
        {
            "title": "Mona Lisa Overdrive",
            "author_id": 1
        }]
    }
]
```

There are a few good reasons for supporting both tables and models in the
fixtures. Using tables is faster since we can rely on SQLAlchemy's bulk insert
to add several records at once. However, to do so, you must first make sure
that the records list is homegenous. In other words, every object in the
`records` list must have the same set of key/value pairs, otherwise the bulk
insert will not work. Using models, however, allows you to have a heterogenous
list of record objects.

The other reason you may want to use models instead of tables is that you'll
be able to take advantage of any python-level defaults, checks, etc. that you
have setup on the model. Using a table, bypasses the model completely and
inserts the data directly into  the database, which means you'll need to think
on a lower level when creating table-based fixtures.

## Usage

To use fixtures in your unit tests, you simply need to create an instance of the
`Fixtures` class and use that to mark the tests where you want to use fixture
data. An instance of `Fixtures` is a decorator that can be used to decorate
methods or classes. When you decorate a method, fixtures will be installed
before the test runs, and torn down after the test finishes. The functions that
setup and teardown fixtures do not interfere with the normal setup and teardown
functions that packages such as unittest, unittest2, and nose provide. In both
cases (setup and teardown) the fixtures are handled first before any user
defined setup/teardown functions are ran. This allows you to  assume that your
fixture data is already in the database when writing your setup functions.

When decorating a class, the fixtures are setup only when the class is created
and torn down after all tests in the class have finished executing. To do this,
the `Fixtures` decorator piggybacks on the `setUpClass` and `tearDownClass`
functions that the unittest library provides. Even though, existing `setUpClass`
and `tearDownClass` methods are replaced when a test class is decorated, this
replacement does not interfere with any of the normal functionality of those
methods. You can still perform any setup and teardown tasks you need to in these
methods, and you can still use `super` to call the setup and teardown methods of
other classes in the [MRO][https://www.python.org/download/releases/2.3/mro]
chain. The only difference is that your fixturs will be inserted into the
database before any other setup happens and removed before any other teardown
tasks occur.

The following code shows an example of how to setup and use the `Fixtures` class
to add fixtures support to your test code.

```python
import unittest

from myapp import app, db

from flask.ext.fixtures import Fixtures

app.config.from_object('myapp.config.TestConfig')
fixtures = Fixtures(app, db)

# In this example, we'll decorate the entire class. This way the fixtures we
# have in the `foo_tests.yml` file are loaded into the test database at class
# creation time (i.e., before any of our tests are ran) and removed after all
# tests have finished execution.
@fixtures('foo_tests.yml')
class TestFoo(unittest.TestCase, FixturesMixin):
    fixtures = ['foo_test_fixtures.json']

    # Your tests go here
```

And, that's all there is to it, now you just need to go write some tests.
