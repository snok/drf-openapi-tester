import logging
from types import FunctionType
from typing import Callable, Dict, Optional, Union

from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.loaders import DrfYasgSchemaLoader, StaticSchemaLoader

logger = logging.getLogger('django_swagger_tester')


def get_logger(level: str, logger_name: str) -> Callable:
    """
    Return logger.
    :param level: log level
    :param logger_name: logger name
    :return: logger
    """
    if level == 'DEBUG':
        return logging.getLogger(logger_name).debug
    elif level == 'INFO':
        return logging.getLogger(logger_name).info
    elif level == 'WARNING':
        return logging.getLogger(logger_name).warning
    elif level == 'ERROR':
        return logging.getLogger(logger_name).error
    elif level == 'EXCEPTION':
        return logging.getLogger(logger_name).exception
    elif level == 'CRITICAL':
        return logging.getLogger(logger_name).critical
    else:
        raise ImproperlyConfigured(
            f'The log level for the `{logger_name}` logger was set as `{level}` ' f'which is not a valid log level.'
        )


class SwaggerTesterSettings(object):
    """
    Loads and validates the packages Django settings.
    """

    def __init__(self) -> None:
        """
        Initializes tester class with base settings.
        """
        # Initialize required package settings (no defaults)
        self.SCHEMA_LOADER: Optional[Union[StaticSchemaLoader, DrfYasgSchemaLoader]] = None

        # Initialize optional package settings (initialized with default settings)
        self.MIDDLEWARE: Dict[str, str] = {'LOG_LEVEL': 'ERROR', 'MODE': 'NORMAL'}
        self.CASE_CHECKER: Optional[Callable] = None
        self.MIDDLEWARE_LOGGER: Optional[Callable] = None
        self.CAMEL_CASE_PARSER = False

        django_settings = self.get_package_settings()
        self.set_package_settings(django_settings)
        self.validate_case_checker_setting()
        self.validate_camel_case_parser_setting()
        self.validate_middleware_settings()
        self.validate_schema_loader(django_settings)

    @staticmethod
    def get_package_settings() -> dict:
        """
        Loads the SWAGGER_TESTER settings from the Django application's settings.py
        """
        from django.conf import settings as django_settings

        if not hasattr(django_settings, 'SWAGGER_TESTER'):
            raise ImproperlyConfigured(
                'Please configure SWAGGER_TESTER in your settings ' 'or remove django-swagger-tester as a dependency'
            )
        return django_settings.SWAGGER_TESTER

    def set_package_settings(self, django_settings) -> None:
        """
        Writes SWAGGER_TESTER attributes to the class' setting variables.
        """
        for setting, value in django_settings.items():
            if hasattr(self, setting):
                setattr(self, setting, value)

    def validate_case_checker_setting(self) -> None:
        """
        Make sure we receive a callable or a None.
        """
        if self.CASE_CHECKER is not None and not isinstance(self.CASE_CHECKER, FunctionType):
            logger.error('CASE_CHECKER setting is misspecified.')
            raise ImproperlyConfigured(
                f'The django-swagger-tester CASE_CHECKER settings is misspecified. '
                f'Valid inputs include None or a callable function.\n\n'
                f'Package supported case checkers can be imported from django_swagger_tester.case_checkers'
            )
        elif self.CASE_CHECKER is None:
            # If None is passed, we want to do nothing when self.CASE_CHECKER is called, so we just assign a lambda expression
            self.CASE_CHECKER = lambda: None

    def validate_camel_case_parser_setting(self) -> None:
        """
        Make sure CAMEL_CASE_PARSER is a boolean, and that the required dependencies are installed if set to True.
        """
        if not isinstance(self.CAMEL_CASE_PARSER, bool):
            raise ImproperlyConfigured(
                '`CAMEL_CASE_PARSER` needs to be True or False, or unspecified (defaults to False).'
            )
        if self.CAMEL_CASE_PARSER:
            try:
                import djangorestframework_camel_case  # noqa: F401
            except ImportError:
                raise ImproperlyConfigured(
                    'The package `djangorestframework_camel_case` is not installed, '
                    'and is required to enable camel case parsing.'
                )

    def validate_middleware_settings(self) -> None:
        """
        Sets and validates middleware settings.
        """
        if self.MIDDLEWARE is None or isinstance(self.MIDDLEWARE, dict) and not self.MIDDLEWARE:
            self.MIDDLEWARE = {'LOG_LEVEL': 'ERROR', 'MODE': 'NORMAL'}
        elif not isinstance(self.MIDDLEWARE, dict):
            raise ImproperlyConfigured('MIDDLEWARE setting needs to be a dictionary or None')
        else:
            # Set the MIDDLEWARE_LOGGER
            if 'LOG_LEVEL' not in self.MIDDLEWARE:
                self.MIDDLEWARE['LOG_LEVEL'] = 'ERROR'
            self.MIDDLEWARE_LOGGER = get_logger(self.MIDDLEWARE['LOG_LEVEL'], 'django_swagger_tester')

            # Set the middleware MODE
            if 'MODE' not in self.MIDDLEWARE:
                self.MIDDLEWARE['MODE'] = 'NORMAL'
            if not isinstance(self.MIDDLEWARE['MODE'], str) or self.MIDDLEWARE['MODE'].upper() not in [
                'NORMAL',
                'STRICT',
            ]:
                raise ImproperlyConfigured(
                    'The SWAGGER_TESTER middleware mode needs to be set to None, "NORMAL", or "STRICT"'
                )
            self.MIDDLEWARE['MODE'] = self.MIDDLEWARE['MODE'].upper()

    def validate_schema_loader(self, django_settings):
        # ------ Validation first -----
        # Then
        self.SCHEMA_LOADER = self.SCHEMA_LOADER()
        self.SCHEMA_LOADER.validation(package_settings=django_settings)


settings = SwaggerTesterSettings()
