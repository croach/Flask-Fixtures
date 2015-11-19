"""
Flask-Fixtures
--------------

A fixtures library for testing Flask apps.
"""
from __future__ import absolute_import

import os
import subprocess
from setuptools import setup


root_dir = os.path.abspath(os.path.dirname(__file__))
package_dir = os.path.join(root_dir, 'flask_fixtures')


# Try to get the long description from the README file or the module's
# docstring if the README isn't available.
try:
    README = open(os.path.join(root_dir, 'README.rst')).read()
except:
    README = __doc__

install_requires = [
                       'Flask',
                       'Flask-SQLAlchemy',
                       'six'
                   ]
try:
    import importlib
except ImportError:
    install_requires.append('importlib')

setup(
    name='Flask-Fixtures',
    version='0.3.4',
    url='https://github.com/croach/Flask-Fixtures',
    license='MIT License',
    author='Christopher Roach',
    author_email='vthakr@gmail.com',
    maintainer='Christopher Roach',
    maintainer_email='vthakr@gmail.com',
    description='A simple library for adding database fixtures for unit tests using nothing but JSON or YAML.',
    long_description=README,
    # py_modules=['flask_fixtures'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    install_requires=install_requires,
    packages=['flask_fixtures'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing'
    ]
)
