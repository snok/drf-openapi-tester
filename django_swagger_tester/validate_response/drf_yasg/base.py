import difflib
import logging

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from rest_framework.response import Response

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.validate_response.base import SwaggerTestBase

logger = logging.getLogger('django_swagger_tester')


class DrfYasgSwaggerTester(SwaggerTestBase):

    def validation(self) -> None:
        """
        Holds validation and setup logic to run when Django starts.
        """
        try:
            import drf_yasg
        except ModuleNotFoundError:
            raise ImproperlyConfigured('Missing the package `drf_yasg`. Run `pip install drf_yasg` to install it.')
        try:
            import json
        except ModuleNotFoundError:
            raise ImproperlyConfigured('Missing the package `json`. Run `pip install json` to install it.')

        if 'drf_yasg' not in apps.app_configs.keys():
            raise ImproperlyConfigured(
                '`drf_yasg` is missing from INSTALLED_APPS. The package is required for testing dynamic schemas.')

    def load_schema(self) -> None:
        """
        Fetches a dynamically generated OpenAPI schema.

        :return: The section of the schema relevant for testing, dict
        """
        logger.debug('Fetching generated dynamic schema')
        from drf_yasg.openapi import Info
        from drf_yasg.generators import OpenAPISchemaGenerator
        from json import loads, dumps

        # Fetch schema and convert to dict
        schema = OpenAPISchemaGenerator(info=Info(title='', default_version='')).get_schema()
        schema = loads(dumps(schema.as_odict()['paths']))  # Converts OrderedDict to dict

        try:
            closest_match = difflib.get_close_matches(self.resolved_url.route, schema.keys(), 1)
            # Test this section thoroughly
            print(closest_match)
            print(difflib.get_close_matches(self.resolved_url.route, schema.keys()))
            schema = schema[closest_match[0]]
        except KeyError:
            raise SwaggerDocumentationError(
                f'No path found for url `{self.resolved_url.route}`. Valid urls include {", ".join([key for key in schema.keys()])}')

        try:
            schema = schema[self.method.lower()]['responses']
        except KeyError:
            raise SwaggerDocumentationError(
                f'No schema found for method {self.method}. Available methods include '
                f'{", ".join([method.upper() for method in schema.keys() if method.upper() != "PARAMETERS"])}.'
            )

        try:
            schema = schema[f'{self.status_code}']['schema']
        except KeyError:
            raise SwaggerDocumentationError(
                f'No schema found for response code {self.status_code}. Documented responses include '
                f'{", ".join([code for code in schema.keys()])}.'
            )

        self.schema = schema


def validate_response(response: Response, method: str, endpoint_url: str):
    tester_class = DrfYasgSwaggerTester()
    tester_class.validate_response(response=response, method=method, endpoint_url=endpoint_url)
