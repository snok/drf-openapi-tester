import json
import logging
import os

import yaml
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.response import Response

from django_swagger_tester.response_validation.base.base import SwaggerTestBase

logger = logging.getLogger('django_swagger_tester')


class StaticSchemaSwaggerTester(SwaggerTestBase):

    def __init__(self) -> None:
        super().__init__()

    def validation(self) -> None:
        """
        Holds validation and setup logic to run when Django starts.
        """
        try:
            import yaml  # noqa: F401
        except ModuleNotFoundError:
            raise ImproperlyConfigured('The package `PyYAML` is required for parsing yaml files. '
                                       'Please run `pip install PyYAML` to install it.')

        _settings = settings.SWAGGER_TESTER

        if 'PATH' not in _settings or _settings['PATH'] is None:
            logger.error('PATH setting is not specified.')
            raise ImproperlyConfigured(
                f'`PATH` is required when testing static schemas. Please update your SWAGGER_TESTER settings.'
            )
        elif not isinstance(_settings['PATH'], str):
            logger.error('PATH setting is not a string.')
            raise ImproperlyConfigured('`PATH` needs to be a string. Please update your SWAGGER_TESTER settings.')

        self.path = _settings['PATH']

    def _load_schema_file(self) -> dict:
        """
        Fetches OpenAPI schema json or yaml contents from a static local file.

        :param path: Relative or absolute path pointing to the schema
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

    def load_schema(self) -> None:
        """
        Fetches a static OpenAPI schema.

        :return: The section of the schema relevant for testing, dict
        """
        logger.debug('Fetching static schema')

        # Fetch schema as dict
        complete_schema = self._load_schema_file()

        # Set definitions
        self.definitions = complete_schema['definitions'] if 'definitions' in complete_schema else None

        # Create a list of endpoints in the schema, matching our resolved path
        url = self.endpoint_path
        matched = [endpoint for endpoint in [key for key in complete_schema['paths']] if endpoint == url]
        if not matched:
            raise ValueError('Could not match the resolved url to a documented endpoint in the OpenAPI specification')

        # Return the appropriate section
        if self.method.lower() in complete_schema['paths'][url]:
            self.schema = complete_schema['paths'][url][self.method.lower()]['responses'][f'{self.status_code}']['content'][
                'application/json']['schema']
        else:
            logger.error('Schema section for %s does not exist.', self.method)
            raise KeyError(f'The OpenAPI schema has no documented HTTP method called `{self.method}`')


def validate_response(response: Response, method: str, endpoint_url: str, **kwargs) -> None:
    """
    This function verifies that an OpenAPI schema definition matches the an API response.
    It inspects the schema recursively, and verifies that the schema matches the structure of the response at every level.

    :param response: HTTP response
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param endpoint_url: Relative path of the endpoint being tested
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
    """
    tester_class = StaticSchemaSwaggerTester()
    tester_class._validate_response(response=response, method=method, endpoint_url=endpoint_url, **kwargs)
