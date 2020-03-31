import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger('django_swagger_tester')


def load_settings() -> dict:
    """
    Loads and validates Django settings.

    :return: tuple of optional strings: (schema setting, case setting, path)
    """
    defaults = {
        'CASE': 'camel case'
        # <-- Put new default setting values here
    }

    logger.debug('Loading settings.')

    if not hasattr(settings, 'SWAGGER_TESTER'):
        logger.error('SWAGGER_TESTER not found in the projects Django settings.')
        raise ImproperlyConfigured('Please specify SWAGGER_TESTER settings in your settings.py')

    _settings = settings.SWAGGER_TESTER

    for setting, value in _settings.items():
        if setting.upper() in defaults:
            defaults[setting.upper()] = value
        else:
            logger.error('Found an excess key in the SWAGGER_TESTER settings: `%s`.', setting)
            raise ImproperlyConfigured(f'`{setting}` is not a valid setting for the openapi-tester module')

    logger.debug('Validating settings.')

    accepted_cases = ['camel case', 'snake case', 'kebab case', 'pascal case']
    if defaults['CASE'] is None:
        pass

    elif not isinstance(defaults['CASE'], str) or defaults['CASE'] not in accepted_cases:
        logger.error('CASE setting is misspecified.')
        raise ImproperlyConfigured(
            f'The openapi-tester package currently doesn\'t support a case called {defaults["CASE"]}.'
            f' Set case to `snake case` for snake_case, '
            f'`camel case` for camelCase, '
            f'`pascal case` for PascalCase,'
            f'`kebab case` for kebab-case, '
            f'or to `None` to skip case validation completely.'
        )

    return defaults


load_settings()
