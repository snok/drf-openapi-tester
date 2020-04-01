import logging

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger('django_swagger_tester')


class SwaggerTesterSettings(object):
    """
    Loads and validates the packages Django settings.
    """

    def __init__(self) -> None:
        """
        Initializes tester class with base settings.
        """
        self.CASE = 'camel case'

        if not hasattr(django_settings, 'SWAGGER_TESTER'):
            return

        logger.debug('Loading settings.')
        _settings = django_settings.SWAGGER_TESTER

        for setting, value in _settings.items():
            if hasattr(self, setting):
                setattr(self, setting, value)
            else:
                logger.error('Found an excess key in the SWAGGER_TESTER settings: `%s`.', setting)
                raise ImproperlyConfigured(f'`{setting}` is not a valid setting for the django-swagger-tester module')

        logger.debug('Validating settings.')
        accepted_cases = ['camel case', 'camelCase', 'snake case', 'snake_case', 'kebab case', 'kebab-case', 'pascal case', 'PascalCase']
        if self.CASE is None:
            pass  # <-- we skip case checks when CASE is None
        elif not isinstance(self.CASE, str) or self.CASE not in accepted_cases:
            logger.error('CASE setting is misspecified.')
            raise ImproperlyConfigured(
                f'The django-swagger-tester package currently doesn\'t support a case called {self.CASE}.'
                f' Set case to `snake case` for snake_case, '
                f'`camel case` for camelCase, '
                f'`pascal case` for PascalCase,'
                f'`kebab case` for kebab-case, '
                f'or to `None` to skip case validation outright.'
            )


settings = SwaggerTesterSettings()
