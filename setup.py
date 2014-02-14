"""
Flask-Fixtures
--------------

A fixtures library for unit testing Flask apps.
"""

from setuptools import setup


setup(
    name='Flask-Fixtures',
    version='0.1',
    url='http://github.com/flask_fixtures',
    license='BSD',
    author='Christopher Roach',
    author_email='vthakr@gmail.com',
    description='A fixtures library for unit testing Flask apps.',
    long_description=__doc__,
    py_modules=['flask_fixtures'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_sqlite3'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'SQLAlchemy'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing'
    ]
)