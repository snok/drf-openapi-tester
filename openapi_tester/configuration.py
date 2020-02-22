import logging
import os.path
from typing import Tuple, Union

from django.conf import settings

from .exceptions import ImproperlyConfigured

logger = logging.getLogger('openapi_tester')


def load_settings() -> Tuple[str, Union[str, None], Union[str, None]]:
    """
    Loads and validates Django settings.

    :return: tuple of strings (path, case)
    """
    config = {'SCHEMA': 'dynamic', 'CASE': 'camel case', 'PATH': None}  # Defaults
    return _validate_settings(_load_django_settings(config))


def _load_django_settings(config: dict) -> dict:
    """
    Assigns Django setting values to schema, case, and path.

    :param config: dict
    :return: dict
    """
    logger.debug('Collecting settings.')

    # Check that the settings are defined
    if not hasattr(settings, 'OPENAPI_TESTER'):
        logger.error('OPENAPI_TESTER not found in the projects Django settings.')
        raise ImproperlyConfigured('Please specify OPENAPI_TESTER settings in your settings.py')

    _settings = settings.OPENAPI_TESTER

    for setting, value in _settings.items():
        if setting in config:
            config[setting] = value
        else:
            logger.error('Excess setting, `%s`, found in OPENAPI_TESTER settings.', setting)
            raise ImproperlyConfigured(f'`{setting}` is not a valid setting for the openapi-tester module')

    return config


def _validate_settings(config: dict) -> Tuple[str, Union[str, None], Union[str, None]]:
    """
    Validates path and case values.

    :param config: dict
    :return: tuple of strings (schema, case, path)
    """
    logger.debug('Validating settings.')

    # Make sure schema is correctly specified - default is "dynamic", so a None value would mean it was set as None
    if not config['SCHEMA'] or not isinstance(config['SCHEMA'], str) or config['SCHEMA'] not in ['dynamic', 'static']:
        logger.error('Required parameter, `SCHEMA`, was mis-specified in the OPENAPI_TESTER settings.')
        raise ImproperlyConfigured(
            f'`SCHEMA` needs to be set to `dynamic` or `static` in the openapi-tester module. '
            f'Please update your OPENAPI_TESTER settings.'
        )

    # Make sure case is correctly specified - default is "camel case"
    accepted_cases = ['camel case', 'snake case', 'kebab case', 'pascal case', None]
    if config['CASE'] is None:
        pass
    elif not isinstance(config['CASE'], str) or config['CASE'] not in accepted_cases:
        logger.error('Required parameter, `CASE`, was mis-specified in the OPENAPI_TESTER settings.')
        raise ImproperlyConfigured(
            f'The openapi-tester package currently doesn\'t support a case called {config["CASE"]}.'
            f' Set case to `snake case` for snake_case, '
            f'`camel case` for camelCase, '
            f'`pascal case` for PascalCase,'
            f'`kebab case` for kebab-case, or None to skip case validation completely.'
        )

    if config['SCHEMA'] == 'static' and config['PATH'] is None:
        logger.error('Required parameter, `PATH`, not specified in the OPENAPI_TESTER settings.')
        raise ImproperlyConfigured(
            f'`PATH` is a required setting for the openapi-tester module. ' f'Please update your OPENAPI_TESTER settings.'
        )
    elif config['SCHEMA'] == 'static':
        if not isinstance(config['PATH'], str):
            logger.error('Parameter `PATH` set as an illegal value.')
            raise ImproperlyConfigured('`PATH` needs to be a string. Please update your OPENAPI_TESTER settings.')

        if not os.path.isfile(config['PATH']):
            logger.error('Path %s does not resolve as a valid file.', config['PATH'])
            raise ImproperlyConfigured(
                f'The path "{config["PATH"]}" does not point to a valid file. Make sure to point to the specification file.'
            )
        elif '.yaml' not in config['PATH'] and '.yml' not in config['PATH'] and '.json' not in config['PATH']:
            logger.error('Path does not include a file type, e.g., `.json` or `.yml`.')
            raise ImproperlyConfigured(
                f'The path "{config["PATH"]}" must point to a yaml or json file. '
                f'Make sure to include the file extension if it is missing from your PATH setting.'
            )

    return config['SCHEMA'].lower(), config['CASE'].lower() if config['CASE'] else None, config['PATH'].lower() if config['PATH'] else None
