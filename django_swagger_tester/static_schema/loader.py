import json
import logging
import os
from typing import Optional

import yaml
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.input_validation.utils import get_request_body
from django_swagger_tester.response_validation.utils import get_response_schema
from django_swagger_tester.utils import resolve_path, validate_inputs

logger = logging.getLogger('django_swagger_tester')


# noinspection PyMethodMayBeStatic
class LoadStaticSchema:
    def __init__(self, route: str, method: str, status_code: Optional[int] = None, **kwargs) -> None:
        """
        Loads OpenAPI schema from a static file.

        :param route: a django-resolved endpoint path
        :param status_code: the relevant HTTP response status code to check in the OpenAPI schema
        :param method: the relevant HTTP method to check in the OpenAPI schema
        """
        validate_inputs(route=route, status_code=status_code, method=method)
        package_settings = settings.SWAGGER_TESTER
        self.validation(package_settings)
        self.path = package_settings['PATH']

        self.route = resolve_path(route)
        self.status_code = status_code
        self.method = method

    def validation(self, package_settings: dict) -> None:
        """
        Before trying to load static schema, we need to verify that:
        - The path to the static file is provided, and that the file type is compatible (json/yml/yaml)
        - The right parsing library is installed (pyYAML for yaml, json is builtin)
        """
        if 'PATH' not in package_settings or package_settings['PATH'] is None:
            logger.error('PATH setting is not specified.')
            raise ImproperlyConfigured(
                f'`PATH` is required when testing static schemas. Please update your SWAGGER_TESTER settings.'
            )
        elif not isinstance(package_settings['PATH'], str):
            logger.error('PATH setting is not a string.')
            raise ImproperlyConfigured('`PATH` needs to be a string. Please update your SWAGGER_TESTER settings.')
        if '.yml' in package_settings['PATH'] or '.yaml' in package_settings['PATH']:
            try:
                import yaml  # noqa: F401
            except ModuleNotFoundError:
                raise ImproperlyConfigured(
                    'The package `PyYAML` is required for parsing yaml files. '
                    'Please run `pip install PyYAML` to install it.'
                )

    def get_schema(self) -> dict:
        """
        Loads a static OpenAPI schema from file, and parses it to a python dict.

        :return: Schema contents as a dict
        :raises: ImproperlyConfigured
        """
        if not os.path.isfile(self.path):
            logger.error('Path `%s` does not resolve as a valid file.', self.path)
            raise ImproperlyConfigured(
                f'The path `{self.path}` does not point to a valid file. Make sure to point to the specification file.'
            )
        try:
            logger.debug('Fetching static schema from %s', self.path)
            with open(self.path, 'r') as f:
                content = f.read()
        except Exception as e:
            logger.exception('Exception raised when fetching OpenAPI schema from %s. Error: %s', self.path, e)
            raise ImproperlyConfigured(
                f'Unable to read the schema file. Please make sure the path setting is correct.\n\nError: {e}'
            )
        if '.json' in self.path:
            return json.loads(content)
        elif '.yaml' in self.path or '.yml' in self.path:
            return yaml.load(content, Loader=yaml.FullLoader)
        else:
            raise ImproperlyConfigured('The specified file path does not seem to point to a JSON or YAML file.')

    def get_response_schema(self) -> dict:
        """
        Indexes schema by url, HTTP method, and status code to get the section of a schema related to a specific response.
        """
        schema = self.get_schema()
        return get_response_schema(schema=schema, method=self.method, status_code=self.status_code, route=self.route)

    def get_request_body(self) -> dict:
        """
        Indexes schema by url, HTTP method, and status code,
        to get the request body of the section of a schema related to an endpoint.
        """
        schema = self.get_schema()
        return get_request_body(schema=schema, method=self.method, route=self.route)
