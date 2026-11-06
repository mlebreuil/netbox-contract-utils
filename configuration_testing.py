###################################################################
#  This file serves as a base configuration for testing purposes  #
#  only. It is not intended for production use.                   #
###################################################################

# Dev container version of the configuration used by CI (netbox-contract/testing/configuration.py):
# - the database credentials come from the environment (.devcontainer/.env), not from the file
# - the hosts are the compose services "db" and "redis"
# - the tests use their own Redis databases (see REDIS below)

import os

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        # The test database is created by Django as test_<NAME>: the user needs CREATEDB (database_init.py does it)
        'NAME': os.environ.get('NETBOX_DB_NAME', 'netbox'),
        'USER': os.environ.get('NETBOX_DB_USER', 'netbox'),
        'PASSWORD': os.environ['NETBOX_DB_PASSWORD'],
        'HOST': 'db',
        'PORT': '',
        'CONN_MAX_AGE': 300,
    }
}

FIELD_CHOICES = {
    'netbox_contract.Contract.internal_party': (
        ('default', 'Default entity', 'green'),
        ('entity1', 'Entity 1', 'green'),
        ('entity2', 'Entity 2', 'yellow'),
    ),
    'netbox_contract.Contract.currency': (
        ('usd', 'USD'),
        ('eur', 'EUR'),
        ('chf', 'CHF'),
        ('pln', 'PLN'),
    ),
    'netbox_contract.Contract.status': (
        ('active', 'Active', 'green'),
        ('canceled', 'Canceled', 'red'),
    ),
}

PLUGINS = [
    'netbox.tests.dummy_plugin',
    'netbox_contract',
]

PLUGINS_CONFIG = {
    'netbox_contract': {
        'top_level_menu': True,
        'mandatory_contract_fields': [],
        'hidden_contract_fields': [],
        'mandatory_invoice_fields': [],
        'hidden_invoice_fields': [],
    }
}

RQ = {
    'COMMIT_MODE': 'auto',
}

# The tests flush the task queue (flushdb) and clear the cache. Use Redis databases 2 and 3 so that a test run does not
# wipe the queue and the cache (databases 0 and 1) of the development server.
REDIS = {
    'tasks': {
        'HOST': 'redis',
        'PORT': 6379,
        'USERNAME': '',
        'PASSWORD': '',
        'DATABASE': 2,
        'SSL': False,
    },
    'caching': {
        'HOST': 'redis',
        'PORT': 6379,
        'USERNAME': '',
        'PASSWORD': '',
        'DATABASE': 3,
        'SSL': False,
    }
}

# Test values published in NetBox's own configuration_testing.py: they protect nothing.
# The development secrets are in .devcontainer/.env and are never used here.
SECRET_KEY = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

DEFAULT_PERMISSIONS = {}

API_TOKEN_PEPPERS = {
    1: 'TEST-VALUE-DO-NOT-USE-TEST-VALUE-DO-NOT-USE-TEST-VALUE-DO-NOT-USE',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True
}
