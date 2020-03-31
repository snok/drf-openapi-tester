import json
import logging
import os

import yaml
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import get_script_prefix
from rest_framework.response import Response

from django_swagger_tester.validate_responses.base import SwaggerTestBase

logger = logging.getLogger('django_swagger_tester')


class StaticSchemaSwaggerTester(SwaggerTestBase):

    def __init__(self):
        self.path = None
        super().__init__()

    def validation(self) -> None:
        """
        Holds validation and setup logic to run when Django starts.
        """
        try:
            import json
        except ModuleNotFoundError:
            raise ImproperlyConfigured('Missing the package `json`. Run `pip install json` to install it.')
        try:
            import yaml
        except ModuleNotFoundError:
            raise ImproperlyConfigured('Missing the package `yaml`. Run `pip install yaml` to install it.')

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

    def load_schema_file(self) -> dict:
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
                f'Could not read the openapi specification. Please make sure the path setting is correct.\n\nError: {e}')

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
        complete_schema = self.load_schema_file()
        # TODO: Test this thoroughly
        url = get_script_prefix() + self.resolved_url.route
        logger.debug('Collecting %s %s section of the OpenAPI schema.', self.method, url)

        # Create a list of endpoints in the schema, matching our resolved path
        matching_endpoints = [endpoint for endpoint in [key for key in complete_schema['paths']] if endpoint in url]
        if len(matching_endpoints) == 0:
            raise ValueError('Could not match the resolved url to a documented endpoint in the OpenAPI specification')
        else:
            matched_endpoint = matching_endpoints[0]

        # Return the appropriate section
        if self.method.lower() in complete_schema['paths'][matched_endpoint]:
            self.schema = complete_schema['paths'][matched_endpoint][self.method.lower()]['responses'][f'{self.status_code}']['content'][
                'application/json']['schema']
        else:
            logger.error('Schema section for %s does not exist.', self.method)
            raise KeyError(f'The OpenAPI schema has no method called `{self.method}`')


def validate_response(response: Response, method: str, endpoint_url: str):
    tester_class = StaticSchemaSwaggerTester()
    tester_class.validate_response(response=response, method=method, endpoint_url=endpoint_url)
