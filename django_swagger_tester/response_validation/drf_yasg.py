import difflib
import logging
import re

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from rest_framework.response import Response

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.response_validation.base.base import SwaggerTestBase

logger = logging.getLogger('django_swagger_tester')


# noinspection PyMethodMayBeStatic
class DrfYasgSwaggerTester(SwaggerTestBase):

    def validation(self) -> None:
        """
        Holds validation and setup logic to run when Django starts.

        For drf_yasg-generated schemas we need to verify that:

        1. The package is installed
        2. Json is installed, for parsing the schema
        3. drf_yasg is in the projects installed_apps
        """
        try:
            import drf_yasg  # noqa: F401
        except ModuleNotFoundError:
            raise ImproperlyConfigured('The package `drf_yasg` is required. Please run `pip install drf_yasg` to install it.')

        if 'drf_yasg' not in apps.app_configs.keys():
            raise ImproperlyConfigured(
                'The package `drf_yasg` is missing from INSTALLED_APPS. Please add it in your '
                '`settings.py`, as it is required for this implementation')

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

        # Index by route
        try:
            dynamic_urls = re.findall(r'\/<\w+:\w+>\/', self.resolved_url)
            if not dynamic_urls:
                closest_match = difflib.get_close_matches(self.resolved_url, schema.keys(), 1)
                schema = schema[closest_match[0]]
            else:
                for dynamic_url in dynamic_urls:
                    logger.debug('Converting self.resolved url: %s', self.resolved_url)
                    logger.debug('Dynamic url: %s', dynamic_url)
                    keyword = dynamic_url[dynamic_url.index('<') + 1: dynamic_url.index(':')]
                    self.resolved_url = self.resolved_url.replace(
                        f'<{keyword}:{keyword}>',
                        f'{{{keyword}}}'
                    )
                    logger.debug('Converted self.resolved_url to %s', self.resolved_url)
                    closest_match = difflib.get_close_matches(self.resolved_url, schema.keys(), 1)
                    logger.debug('Indexing schema by closest match: %s', closest_match)
                    schema = schema[closest_match[0]]
            # For future reference: not sure about this implementation - we should look to change it for something 100% reliable.
            # What we're doing here, is letting difflib match our resolved route, to the schema, using probabilities.

            logger.debug('Closest match: %s', closest_match)
        except KeyError:
            raise SwaggerDocumentationError(
                f'Failed initialization\n\nError: Unsuccessfully tried to index the OpenAPI schema by `{closest_match[0]}` '
                f'based on the resolved url `/{self.resolved_url}`, but the key does not exist in the schema.'
                f'\n\nFor debugging purposes: valid urls include {", ".join([key for key in schema.keys()])}')

        # Index by method and responses
        try:
            schema = schema[self.method.lower()]['responses']
        except KeyError:
            raise SwaggerDocumentationError(
                f'No schema found for method {self.method}. Available methods include '
                f'{", ".join([method.upper() for method in schema.keys() if method.upper() != "PARAMETERS"])}.'
            )

        # Index by status and schema
        try:
            schema = schema[f'{self.status_code}']['schema']
        except KeyError:
            raise SwaggerDocumentationError(
                f'No schema found for response code `{self.status_code}`. Documented responses include '
                f'{", ".join([code for code in schema.keys()])}.'
            )

        self.schema = schema


def validate_response(response: Response, method: str, endpoint_url: str, **kwargs) -> None:
    """
    This function verifies that an OpenAPI schema definition matches the an API response.
    It inspects the schema recursively, and verifies that the schema matches the structure of the response at every level.

    :param response: HTTP response
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param endpoint_url: Relative path of the endpoint being tested
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
    """
    tester_class = DrfYasgSwaggerTester()
    tester_class._validate_response(response=response, method=method, endpoint_url=endpoint_url, **kwargs)
