import logging
import os.path
from typing import Tuple

from django.conf import settings

from .exceptions import ImproperlyConfigured

logger = logging.getLogger('openapi-tester')


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
    logger.debug('Collecting settings.')

    # Check that the settings are defined
    if not hasattr(settings, 'OPENAPI_TESTER'):
        logger.error('OPENAPI_TESTER not found in the projects Django settings.')
        raise ImproperlyConfigured('Please specify OPENAPI_TESTER in your settings.py')

    _settings = settings.OPENAPI_TESTER

    for setting, value in _settings.items():
        if setting in config:
            config[setting] = value
        else:
            logger.error('Excess setting, `%s`, found in OPENAPI_TESTER settings.', setting)
            raise ImproperlyConfigured(f'`{setting}` is not a valid setting for the openapi-tester module')

    return config


def _validate_settings(config: dict) -> Tuple[str, str]:
    """
    Validates path and case values.

    :param config: dict
    :return: tuple of strings (path, case)
    """
    logger.debug('Validating settings.')

    # Make sure path is specified
    if config['path'] is None:
        logger.error('Required parameter, `path`, not specified in the OPENAPI_TESTER settings.')
        raise ImproperlyConfigured(f'`path` is a required setting for the openapi-tester module')

    # If it is specified, make sure it's correctly specified
    if not isinstance(config['path'], str):
        logger.error('Parameter `path` set as an illegal value.')
        raise ImproperlyConfigured('`path` needs to be a string')

    if 'http://' in config['path'] or 'https://' in config['path']:
        logger.debug('Parameter `path` seems to point to an URL.')
        pass  # We'll have to try and fetch the schema before we know if the url is correct
    else:
        logger.debug('Parameter `path` seems to point to a local file.')
        if not os.path.isfile(config['path']):
            logger.error('Path %s does not resolve as a valid file.', config['path'])
            raise ImproperlyConfigured(
                f'The path "{config["path"]}" does not point to a valid file. '
                'Make sure to point to the specification file or add a scheme to your url '
                '(e.g., `http://`).'
            )
        elif '.yaml' not in config['path'] and '.yml' not in config['path'] and '.json' not in config['path']:
            logger.error('Path does not include a file type, e.g., `.json` or `.yml`.')
            raise ImproperlyConfigured(
                f'The path "{config["path"]}" must point to a yaml or json file. Make sure to include the file type if it is missing.'
            )

    supported_cases = ['camel case', 'snake case', None]

    if config['case'] not in supported_cases:
        logger.error('Parameter `case` is invalid.')
        raise ImproperlyConfigured(
            f'This package currently doesn\'t support a case called {config["case"]}.'
            f' Set case to `snake case` for snake_case, '
            f'`camel case` for camelCase, or None to skip case validation completely.'
        )

    return config['path'].lower(), config['case'].lower() if config['case'] else None
