import logging
from typing import Tuple, Union

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger('django_swagger_tester')


def _load_django_settings(config: dict) -> dict:
    """
    Assigns Django setting values to schema, case, and path.

    :param config: default config values
    :return: config with overwritten values from settings.py
    """
    logger.debug('Collecting settings.')

    # Check that the SWAGGER_TESTER object is defined in settings.py
    if not hasattr(settings, 'SWAGGER_TESTER'):
        logger.error('SWAGGER_TESTER not found in the projects Django settings.')
        raise ImproperlyConfigured('Please specify SWAGGER_TESTER settings in your settings.py')
    else:
        _settings = settings.SWAGGER_TESTER

    # Assign the specified values to the config-dict - overwrite existing values
    for setting, value in _settings.items():
        if setting.upper() in config:
            config[setting.upper()] = value
        else:
            logger.error('Found an excess key in the SWAGGER_TESTER settings: `%s`.', setting)
            raise ImproperlyConfigured(f'`{setting}` is not a valid setting for the openapi-tester module')

    return config


def _validate_settings(config: dict) -> Tuple[str, Union[str, None], Union[str, None]]:
    """
    Validates settings.

    :param config: package settings, dict
    :return: Tuple of 3 strings/optional strings
            - schema setting ("dynamic" or "static"),
            - case setting (e.g., "camel case"),
            - and path (file path if schema setting is static, else None)
    """
    logger.debug('Validating settings.')

    # Make sure schema is correctly specified
    # The default schema value is "dynamic", so a `None` would only be set if it was overwritten by the project settings
    schema_is_none = not config['SCHEMA'] or not isinstance(config['SCHEMA'], str)
    if schema_is_none or config['SCHEMA'].lower() not in ['dynamic', 'static']:
        logger.error('SCHEMA setting is mis-specified. Needs to be "dynamic" or "static", not %s', config['SCHEMA'])
        raise ImproperlyConfigured(
            f'`SCHEMA` needs to be set to `dynamic` or `static` in the openapi-tester module, '
            f'not {config["SCHEMA"]}. Please update your SWAGGER_TESTER settings.'
        )

    # Make sure the case setting is correctly specified
    # The default case value "camel case"
    accepted_cases = ['camel case', 'snake case', 'kebab case', 'pascal case']
    if config['CASE'] is None:
        pass
    elif not isinstance(config['CASE'], str) or config['CASE'] not in accepted_cases:
        logger.error('CASE setting is mis-specified.')
        raise ImproperlyConfigured(
            f'The openapi-tester package currently doesn\'t support a case called {config["CASE"]}.'
            f' Set case to `snake case` for snake_case, '
            f'`camel case` for camelCase, '
            f'`pascal case` for PascalCase,'
            f'`kebab case` for kebab-case, '
            f'or to `None` to skip case validation completely.'
        )

    # Make sure the path to an openapi schema is specified if the SCHEMA is set to `static`
    if config['SCHEMA'] == 'static':
        if config['PATH'] is None:
            logger.error('PATH setting is not specified.')
            raise ImproperlyConfigured(
                f'`PATH` is a required setting for the django-swagger-tester module. Please update your SWAGGER_TESTER settings.'
            )
        elif not isinstance(config['PATH'], str):
            logger.error('PATH setting is not a string.')
            raise ImproperlyConfigured('`PATH` needs to be a string. Please update your SWAGGER_TESTER settings.')
        else:
            from django_swagger_tester.static.get_schema import fetch_from_dir

            fetch_from_dir(config['PATH'])

    # Make sure drf-yasg is installed for dynamic schemas
    elif config['SCHEMA'] == 'dynamic':
        if 'drf_yasg' not in apps.app_configs.keys():
            raise ImproperlyConfigured(
                '`drf_yasg` is missing from INSTALLED_APPS. ' 'The package is required for testing dynamic schemas.')
    return (
        config['SCHEMA'].lower(),
        config['CASE'].lower() if config['CASE'] else None,
        config['PATH'].lower() if config['PATH'] else None,
    )


def load_settings() -> Tuple[str, Union[str, None], Union[str, None]]:
    """
    Loads and validates Django settings.

    :return: tuple of optional strings: (schema setting, case setting, path)
    """
    defaults = {'SCHEMA': 'dynamic', 'CASE': 'camel case', 'PATH': None}
    return _validate_settings(_load_django_settings(defaults))
