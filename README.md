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
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
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

Given the classes above, if we wanted to mock up some data for our database, we
could do so in single file, or we could even split our fixtures into multiple
files each corresponding to each of our classes. For this simple example, we'll
go with one file that we'll call authors.json.

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

To use Flask-Fixtures in your unit tests, you'll need to make sure your test
class inherits from `FixturesMixin` and that you've specified a list of
fixtures files to load.The sample code below shows how to do each these steps.

First, make sure the app that you're testing is initialized with the proper
configuration. Then import and initialize the `FixturesMixin` class, create a
new test class, and inherit from `FixturesMixin`. Now you just need to tell
Flask-Fixtures which fixtures files to use for your tests. You can do so by
setting either the `class_fixtures` or `fixtures` class variable. The former
will setup fixtures only when the class is created, whereas the latter is
setup and torn down between each test. The `fixtures` and `class_fixtures`
variables should be set to a list of strings, each of which is a name of a
fixtures file to load. Flask-Fixtures will then search each directory in the
`FIXTURES_DIRS` config variable, in order, for a file matching each name in
the list and load each into the test database.

```python
import unittest

from flask.ext.fixtures import FixturesMixin

app.config.from_object('hirein.config.TestConfig')
FixturesMixin.init_app(app, db)


class TestFoo(unittest.TestCase, FixturesMixin):
    fixtures = ['foo_test_fixtures.json']

    # Your tests go here
```

And, that's all there is to it, now you need to write some tests.
