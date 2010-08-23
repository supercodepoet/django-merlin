from django.core.management import setup_environ

from merlin.tests.fixtures.testproject import settings

setup_environ(settings)

from django.test import utils
from django.db import connection

def setup_package(module):
    utils.setup_test_environment()
    module._old_db_name = connection.creation.create_test_db(verbosity=1)

def teardown_package(module):
    connection.creation.destroy_test_db(module._old_db_name)
    utils.teardown_test_environment()

