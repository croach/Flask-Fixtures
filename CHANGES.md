Changes
=======

0.1.0
-----

- Initial commit

0.2.0
-----

- Refactored. Now decorator based, previously it was based on
  inheritance and worked more like Django's fixtures. This way seems
  to fit with the way Flask does extensions a bit better and also
  makes the underlying code much cleaner and easier to maintain (it
  used to rely on metaclass magic to do everything).

0.3.0 (April 8, 2014)
---------------------

- The default behavior of the Fixtures decorator is now to search for
  a fixtures file in the same directory as the test module with a
  matching name in one of the supported file formats.

- Refactored the fixtures loaders into a separate module that makes it
  easier to add support for new file formats. To do so simply add a
  new class to the loaders.py module that inherits from the
  FixtureLoader abstract base class and add a class variable
  `extensions` that is a list of supported extensions and implement a
  `load` method that takes a filename and returns a python object.