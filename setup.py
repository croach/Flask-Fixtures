"""
Flask-Fixtures
--------------

A fixtures library for testing Flask apps.
"""

import os
import subprocess
from setuptools import setup


root_dir = os.path.abspath(os.path.dirname(__file__))
package_dir = os.path.join(root_dir, 'flask_fixtures')


# Try to get the long description from the README file or the module's
# docstring if the README isn't available.
try:
    README = open(os.path.join(root_dir, 'README.md')).read()
except:
    README = __doc__

# Try to read in the change log as well
try:
    CHANGES = open(os.path.join(root_dir, 'CHANGES.md')).read()
except:
    CHANGES = ''

setup(
    name='Flask-Fixtures',
    version='0.3.0',
    url='http://github.com/flask_fixtures',
    license='Apache License 2.0',
    author='Christopher Roach',
    author_email='vthakr@gmail.com',
    maintainer='Christopher Roach',
    maintainer_email='vthakr@gmail.com',
    description='A fixtures library for testing Flask apps.',
    long_description=README + '\n\n' + CHANGES,
    # py_modules=['flask_fixtures'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    packages=['flask_fixtures'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask-SQLAlchemy'
    ],
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