import json
import logging
import os

import yaml
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.response_validation.base import get_response_schema
from django_swagger_tester.utils import validate_method

logger = logging.getLogger('django_swagger_tester')


# noinspection PyMethodMayBeStatic
class LoadStaticSchema:

    def __init__(self, route, status_code, method) -> None:
        """
        Loads the drf_yasg-generated OpenAPI schema, and resolves the endpoint_url.

        :param schema: Complete OpenAPI schema
        :param path: A drf_yasg-schema-compatible path (see get_drf_yasg_compatible_route)
        :param method: The relevant HTTP method
        :param status code: The HTTP response status code
        """
        assert validate_method(method), '`method` is invalid.'
        assert isinstance(status_code, int), '`status_code` should be an integer.'
        assert 100 <= status_code <= 505, '`status_code` should be a valid HTTP response code.'

        package_settings = settings.SWAGGER_TESTER
        self._validation(package_settings)

        self.path = package_settings['PATH']
        self.status_code = status_code
        self.method = method
        self.route = route

    def _validation(self, package_settings: dict) -> None:
        """
        For static schemas, it's important that we verify:
        1. Path to static file is provided, and is the right type
        2. pyYAML is installed, if the path ends in .yml or .yaml
        2. Json is installed, for parsing the schema
        3. drf_yasg is in the projects installed_apps
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
                raise ImproperlyConfigured('The package `PyYAML` is required for parsing yaml files. '
                                           'Please run `pip install PyYAML` to install it.')

    def _load_schema_file_contents(self) -> dict:
        """
        Fetches OpenAPI schema json or yaml contents from a static local file.

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
                f'Unable to read the schema file. Please make sure the path setting is correct.\n\nError: {e}')

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
        schema = self._load_schema_file_contents()
        get_response_schema(schema=schema, method=self.method, status_code=self.status_code, route=self.route)
