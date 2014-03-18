"""
Flask-Fixtures
--------------

A fixtures library for testing Flask apps.
"""

import os
from setuptools import setup


root_dir = os.path.abspath(os.path.dirname(__file__))

try:
  README = open(os.path.join(root_dir, 'README.md')).read()
except:
  README = __doc__

setup(
    name='Flask-Fixtures',
    version='0.1',
    url='http://github.com/flask_fixtures',
    license='Apache License 2.0',
    author='Christopher Roach',
    author_email='vthakr@gmail.com',
    maintainer='Christopher Roach',
    maintainer_email='vthakr@gmail.com',
    description='A fixtures library for testing Flask apps.',
    long_description=README,
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