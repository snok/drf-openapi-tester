import logging
from json import dumps, loads

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from rest_framework.response import Response

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.response_validation.base.base import SwaggerTestBase
from django_swagger_tester.utils import convert_resolved_url, get_paths

logger = logging.getLogger('django_swagger_tester')


# noinspection PyMethodMayBeStatic
class DrfYasgSwaggerTester(SwaggerTestBase):

    def __init__(self) -> None:
        super().__init__()
        from drf_yasg.openapi import Info
        from drf_yasg.generators import OpenAPISchemaGenerator
        self.schema_generator = OpenAPISchemaGenerator(info=Info(title='', default_version=''))

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

        # Fetch schema and convert to dict
        complete_odict_schema = self.schema_generator.get_schema(None, True)
        complete_schema = loads(dumps(complete_odict_schema.as_odict()))  # Converts OrderedDict to dict

        # Set definitions
        self.definitions = complete_schema['definitions'] if 'definitions' in complete_schema else None

        # drf_yasg finds a common denominator for paths, and cuts that out of the openapi schema
        # For example, /api/v1/... might then become /v1/...
        # This is a bit tricky to deal with, because static schema generation doesnt
        path_prefix = self.schema_generator.determine_path_prefix(get_paths())
        url = convert_resolved_url(self.resolved_url).replace(path_prefix, '')

        # Index by route
        try:
            logger.debug('Indexing schema by route `%s`', url)
            schema = complete_schema['paths'][url]
        except KeyError:
            raise SwaggerDocumentationError(
                f'Failed initialization\n\nError: Unsuccessfully tried to index the OpenAPI schema by '
                f'`{url}`, but the key does not exist in the schema.'
                f'\n\nFor debugging purposes: valid urls include {", ".join([key for key in complete_schema.keys()])}')

        # Index by method and responses
        try:
            logger.debug('Indexing schema by method `%s`', self.method.lower())
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
