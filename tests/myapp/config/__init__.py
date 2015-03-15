class TestConfig(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    testing = True
    debug = True
    FIXTURES_DIRS = ['../../tests/fixtures']