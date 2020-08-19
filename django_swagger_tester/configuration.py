import inspect
import logging
from types import FunctionType
from typing import Callable, List

from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.schema_loaders import _LoaderBase

logger = logging.getLogger('django_swagger_tester')


class MiddlewareSettings(object):
    """
    Holds middleware specific settings.
    """

    def __init__(self, middleware_settings: dict) -> None:
        """
        Initializes tester class with base settings.
        """
        # Define default values for middleware settings
        self.LOG_LEVEL = 'ERROR'
        self.STRICT = False
        self.VALIDATE_RESPONSE = True
        self.VALIDATE_REQUEST_BODY = True
        self.VALIDATION_EXEMPT_URLS: List[str] = []

        # Overwrite defaults
        for setting, value in middleware_settings.items():
            if hasattr(self, setting):
                setattr(self, setting, value)
            else:
                raise ImproperlyConfigured(
                    f'Received excess middleware setting, `{setting}`, for SWAGGER_TESTER. '
                    f'Please correct or remove this from the middleware settings.'
                )

        self.validate_and_set_logger()
        self.validate_bool(self.STRICT, 'STRICT')
        self.validate_bool(self.VALIDATE_REQUEST_BODY, 'VALIDATE_REQUEST_BODY')
        self.validate_bool(self.VALIDATE_RESPONSE, 'VALIDATE_RESPONSE')

    def validate_and_set_logger(self) -> None:
        """
        Makes sure the LOG_LEVEL setting is the right type, and sets LOGGER.

        Bad strings are handled in self.get_logger
        """
        if not isinstance(self.LOG_LEVEL, str):
            raise ImproperlyConfigured(f'The SWAGGER_TESTER middleware setting `LOG_LEVEL` must be a string value')
        self.LOGGER: Callable = self.get_logger(self.LOG_LEVEL.upper(), 'django_swagger_tester')

    @staticmethod
    def validate_bool(value: bool, setting_name: str) -> None:
        """
        Validates a boolean setting.
        """
        if not isinstance(value, bool):
            raise ImproperlyConfigured(
                f'The SWAGGER_TESTER middleware setting `{setting_name}` must be a boolean value'
            )

    @staticmethod
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
                f'The log level for the `{logger_name}` logger was set as `{level}` which is not a valid log level.'
            )


class SwaggerTesterSettings(object):
    """
    Loads and validates the packages Django settings.
    """

    def __init__(self) -> None:  # sourcery skip: remove-redundant-pass
        """
        Initializes tester class with base settings.
        """
        # Get SWAGGER_TESTER settings
        swagger_tester_settings = self.get_package_settings()

        # Required package settings
        self.SCHEMA_LOADER = None

        # Defaulted package settings
        self.CASE_CHECKER: Callable = lambda: None
        self.CAMEL_CASE_PARSER = False
        self.CASE_WHITELIST: List[str] = []

        # Overwrite defaults
        for setting, value in swagger_tester_settings.items():
            if hasattr(self, setting):
                setattr(self, setting, value)
            else:
                # Some loader classes will have extra settings passed to the loader class as kwargs
                # Because of this, we cannot raise errors for extra settings
                pass

        # Load middleware settings as its own class
        self.MIDDLEWARE = MiddlewareSettings(swagger_tester_settings.get('MIDDLEWARE', {}))

        # Make sure schema loader was specified
        self.set_and_validate_schema_loader(swagger_tester_settings)

        # Validate other specified settings to make sure they are valid
        self.validate_case_checker_setting()
        self.validate_camel_case_parser_setting()
        self.validate_case_whitelist()

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
        else:
            from django.conf import settings as django_settings

            if hasattr(django_settings, 'REST_FRAMEWORK') and 'djangorestframework_camel_case.parser' in str(
                django_settings.REST_FRAMEWORK
            ):
                logger.warning(
                    'Found `djangorestframework_camel_case` in REST_FRAMEWORK settings, '
                    'but CAMEL_CASE_PARSER is not set to True'
                )

    def set_and_validate_schema_loader(self, package_settings: dict) -> None:
        """
        Sets self.LOADER_CLASS and validates the setting.
        """
        if self.SCHEMA_LOADER is None:
            raise ImproperlyConfigured('The LOADER_CLASS setting is required')

        if not inspect.isclass(self.SCHEMA_LOADER):
            raise ImproperlyConfigured('The LOADER_CLASS setting must be a class')
        elif not issubclass(self.SCHEMA_LOADER, _LoaderBase):
            raise ImproperlyConfigured(
                'The specified LOADER_CLASS must inherit from django_swagger_tester.schema_loaders._LoaderBase'
            )

        self.LOADER_CLASS: _LoaderBase = self.SCHEMA_LOADER()
        self.LOADER_CLASS.validation(package_settings=package_settings)

    def validate_case_whitelist(self) -> None:
        """
        Validates the case whitelist as a list of strings.
        """
        if self.CASE_WHITELIST is None:
            self.CASE_WHITELIST = []
        if not isinstance(self.CASE_WHITELIST, list):
            raise ImproperlyConfigured('The CASE_WHITELIST setting needs to be a list of strings')
        elif any(not isinstance(item, str) for item in self.CASE_WHITELIST):
            raise ImproperlyConfigured('The CASE_WHITELIST setting list can only contain strings')


settings = SwaggerTesterSettings()
