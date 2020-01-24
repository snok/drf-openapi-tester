import os.path
from typing import Tuple

from django.conf import settings

from .exceptions import ImproperlyConfigured


def load_settings() -> Tuple[str, str]:
    """
    Loads and validates Django settings.

    :return: tuple of strings (path, case)
    """
    config = {'path': None, 'case': 'camel case'}  # Defaults
    return _validate_settings(_load_django_settings(config))


def _load_django_settings(config: dict) -> dict:
    """
    Assigns Django setting values to path and case.

    :param config: dict
    :return: dict
    """
    # Check that the settings are defined
    if not hasattr(settings, 'OPENAPI_TESTER'):
        raise ImproperlyConfigured('Please specify OPENAPI_TESTER in your settings.py')

    _settings = settings.OPENAPI_TESTER

    for setting, value in _settings.items():
        if setting in config:
            config[setting] = value
        else:
            raise ImproperlyConfigured(f'`{setting}` is not a valid setting for the openapi-tester module')

    return config


def _validate_settings(config: dict) -> Tuple[str, str]:
    """
    Validates path and case values.

    :param config: dict
    :return: tuple of strings (path, case)
    """
    # Make sure path is specified
    if config['path'] is None:
        raise ImproperlyConfigured(f'`path` is a required setting for the openapi-tester module')

    # If it is specified, make sure it's correctly specified
    if not isinstance(config['path'], str):
        raise ImproperlyConfigured('`path` needs to be a string')

    if 'http://' in config['path'] or 'https://' in config['path']:
        pass  # We'll have to try and fetch the schema before we know if the url is correct
    else:
        if not os.path.isfile(config['path']):
            raise ImproperlyConfigured(
                f'The path "{config["path"]}" does not point to a valid file. '
                'Make sure to point to the specification file or add a scheme to your url '
                '(e.g., `http://`).'
            )

    supported_cases = ['camel case', 'snake case', None]

    if config['case'] not in supported_cases:
        raise ImproperlyConfigured(
            f'This package currently doesn\'t support a case called {config["case"]}.'
            f' Set case to `snake case` for snake_case, '
            f'`camel case` for camelCase, or None to skip case validation completely.'
        )

    return config['path'].lower(), config['case'].lower()
