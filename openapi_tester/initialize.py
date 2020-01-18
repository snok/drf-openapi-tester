"""
This file is run on initialization, and will verify that the Django settings are correctly specified.
"""
import logging
import os.path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger('cs-api')

oat_settings = {
    'PATH': None,
    'CASE': 'CAMELCASE',  # Default value
}

supported_cases = ['CAMELCASE', 'SNAKECASE']

# Check that the settings are defined
if not hasattr(settings, 'OPENAPI_TESTER_SETTINGS'):
    raise ImproperlyConfigured('Please specify OPENAPI_TESTER_SETTINGS in your settings.py')

project_settings = settings.OPENAPI_TESTER_SETTINGS

# Check that we've only got the settings we want
for project_setting, value in project_settings.items():
    if project_setting in oat_settings:
        oat_settings[project_setting] = value
    else:
        raise ImproperlyConfigured(f'{project_setting} is not a valid setting for the openapi-tester module')

# Make sure path is specified
if oat_settings['PATH'] is None:
    raise ImproperlyConfigured(f'PATH is a required setting for the openapi-tester module')

# If it is specified, make sure it's correctly specified
if not isinstance(oat_settings['PATH'], str):
    raise ImproperlyConfigured('The path to your swagger specification (file or url) needs to be a string')

if 'http://' in oat_settings['PATH'] or 'https://' in oat_settings['PATH']:
    pass  # We'll have to try and fetch the schema before we know if the address is right or wrong
else:
    if not os.path.isfile(oat_settings['PATH']):
        raise ImproperlyConfigured(
            'The path specified does not point to a valid file. '
            'Make sure to point to the specification file or add a scheme to your url '
            '(e.g., `http://`).'
        )

if not oat_settings['CASE'] in supported_cases and oat_settings['CASE'] is not None:
    raise ImproperlyConfigured(
        f'This package currently doesn\'t support a case called {oat_settings["CASE"]}.'
        f'Specify `SNAKECASE`, `CAMELCASE`, or specify None for skip case validation.'
    )
