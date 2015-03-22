import abc
import os
import logging

logger = logging.getLogger(__name__)

try:
  import simplejson as json
except ImportError:
  import json

try:
  import yaml
except ImportError:
  def load(self, filename):
    raise Exception("Could not load fixture '%s'. Make sure you have PyYAML installed." % filename)
  yaml = type('FakeYaml', (object,), {
    'load': load
  })()


class FixtureLoader(object):
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def load(self):
    pass


class JSONLoader(FixtureLoader):

  extensions = ('.json', '.js')

  def load(self, filename):
    with open(filename) as fin:
      return json.load(fin)


class YAMLLoader(FixtureLoader):

  extensions = ('.yaml', '.yml')

  def load(self, filename):
    with open(filename) as fin:
      return yaml.load(fin)


def load(filename):
  name, extension = os.path.splitext(filename)

  for cls in FixtureLoader.__subclasses__():
    # If a loader class has no extenions, log a warning so the developer knows
    # that it will never be used anyhwhere
    if not hasattr(cls, 'extensions'):
      logger.warn()
      continue

    # Otherwise, check if the file's extension matches a loader extension
    for ext in cls.extensions:
      if extension == ext:
        return cls().load(filename)

  # None of the loaders matched, so raise an exception
  raise Exception("Could not load fixture '%s'. Unsupported file format." % filename)


def extensions():
  return [ext for c in FixtureLoader.__subclasses__() for ext in c.extensions]

