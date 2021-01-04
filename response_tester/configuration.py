import inspect
import logging
from types import FunctionType
from typing import Callable, List

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

import response_tester.type_declarations as td

logger = logging.getLogger('response_tester')


class SwaggerTesterSettings:
    _loader_class: td.BaseSchemaLoader

    @property
    def schema_loader(self):
        return django_settings.RESPONSE_TESTER.get('SCHEMA_LOADER', None)

    @property
    def case_tester(self) -> Callable:
        return django_settings.RESPONSE_TESTER.get('CASE_TESTER', lambda *args: None)

    @property
    def camel_case_parser(self) -> bool:
        return django_settings.RESPONSE_TESTER.get('CAMEL_CASE_PARSER', False)

    @property
    def case_passlist(self) -> List[str]:
        return django_settings.RESPONSE_TESTER.get('CASE_PASSLIST', [])

    @property
    def parameterized_i18n_name(self):
        return django_settings.RESPONSE_TESTER.get('PARAMETERIZED_I18N_NAME', '')

    @property
    def loader_class(self) -> td.BaseSchemaLoader:
        if not hasattr(self, '_loader_class'):
            self.set_and_validate_schema_loader()
        return self._loader_class

    def validate(self):
        if not hasattr(django_settings, 'RESPONSE_TESTER') or not django_settings.RESPONSE_TESTER:
            raise ImproperlyConfigured('RESPONSE_TESTER settings need to be configured')

        self.validate_case_tester_setting()
        self.validate_camel_case_parser_setting()
        self.validate_case_passlist()
        self.set_and_validate_schema_loader()
        self.validate_parameterized_i18n_name()

    def validate_parameterized_i18n_name(self):
        if not isinstance(self.parameterized_i18n_name, str):
            raise ImproperlyConfigured('PARAMETERIZED_I18N_NAME must be a string')

    def validate_case_tester_setting(self) -> None:
        """
        Make sure we receive a callable or a None.
        """
        if self.case_tester is not None and not isinstance(self.case_tester, FunctionType):
            logger.error('CASE_TESTER setting is mis-specified.')
            raise ImproperlyConfigured(
                'The django-openapi-response-tester CASE_TESTER setting is misspecified. '
                'Please pass a case tester callable from response_tester.case_testers, '
                'make your own, or pass `None` to skip case validation.'
            )
        elif self.case_tester is None:
            raise ImproperlyConfigured(
                'The django-openapi-response-tester CASE_TESTER setting cannot be None. Replace it with `lambda: None`'
            )

    def validate_camel_case_parser_setting(self) -> None:
        """
        Make sure CAMEL_CASE_PARSER is a boolean, and that the required dependencies are installed if set to True.
        """
        if not isinstance(self.camel_case_parser, bool):
            raise ImproperlyConfigured('`CAMEL_CASE_PARSER` needs to be True or False')
        if self.camel_case_parser and 'djangorestframework_camel_case' not in django_settings.INSTALLED_APPS:
            raise ImproperlyConfigured(
                'The package `djangorestframework_camel_case` is not installed, '
                'and is required to enable camel case parsing.'
            )
        else:

            if hasattr(django_settings, 'REST_FRAMEWORK') and 'djangorestframework_camel_case.parser' in str(
                django_settings.REST_FRAMEWORK
            ):
                logger.warning(
                    'Found `djangorestframework_camel_case` in REST_FRAMEWORK settings, '
                    'but CAMEL_CASE_PARSER is not set to True'
                )

    def set_and_validate_schema_loader(self) -> None:
        """
        Sets self.loader_class and validates the setting.
        """

        addon = '. Please pass a loader class from response_tester.schema_loaders.'
        if self.schema_loader is None:
            raise ImproperlyConfigured(
                'SCHEMA_LOADER is missing from your RESPONSE_TESTER settings, and is required' + addon
            )

        if not inspect.isclass(self.schema_loader):
            raise ImproperlyConfigured('SCHEMA_LOADER must be a class' + addon)

        self._loader_class = self.schema_loader()

        from .loaders import StaticSchemaLoader

        if isinstance(self._loader_class, StaticSchemaLoader):
            """
            Before trying to load static schema, we need to verify that:
            - The path to the static file is provided, and that the file type is compatible (json/yml/yaml)
            - The right parsing library is installed (pyYAML for yaml, json is builtin)
            """
            path = django_settings.RESPONSE_TESTER.get('PATH', None)
            if not path:
                logger.error('PATH setting is not specified')
                raise ImproperlyConfigured(
                    'PATH is required to load static OpenAPI schemas. Please add PATH to the RESPONSE_TESTER settings.'
                )
            elif not isinstance(path, str):
                logger.error('PATH setting is not a string')
                raise ImproperlyConfigured('`PATH` needs to be a string. Please update your RESPONSE_TESTER settings.')
            if '.yml' in path or '.yaml' in path:
                try:
                    import yaml  # noqa: F401
                except ModuleNotFoundError:
                    raise ImproperlyConfigured(
                        'The package `PyYAML` is required for parsing yaml files. '
                        'Please run `pip install PyYAML` to install it.'
                    )
            self._loader_class.set_path(path)

    def validate_case_passlist(self) -> None:
        """
        Validates the case whitelist as a list of strings.
        """
        if not isinstance(self.case_passlist, list):
            raise ImproperlyConfigured('The CASE_PASSLIST setting needs to be a list of strings')
        elif any(not isinstance(item, str) for item in self.case_passlist):
            raise ImproperlyConfigured('The CASE_PASSLIST setting list can only contain strings')


settings = SwaggerTesterSettings()
