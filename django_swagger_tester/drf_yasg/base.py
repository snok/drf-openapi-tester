import logging
from json import dumps, loads

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.response_validation.base import SwaggerTestBase
from django_swagger_tester.utils import convert_resolved_url, get_paths

logger = logging.getLogger('django_swagger_tester')


# noinspection PyMethodMayBeStatic
class DrfYasgSwaggerTester(SwaggerTestBase):

    def __init__(self, endpoint_url) -> None:
        """
        Loads the drf_yasg-generated OpenAPI schema, and resolves the endpoint_url.
        """
        super().__init__()
        from drf_yasg.openapi import Info
        from drf_yasg.generators import OpenAPISchemaGenerator
        schema_generator = OpenAPISchemaGenerator(info=Info(title='', default_version=''))
        self.drf_yasg_path_prefix = schema_generator.determine_path_prefix(get_paths())
        odict_schema = schema_generator.get_schema(None, True)
        self.schema = loads(dumps(odict_schema.as_odict()))  # Converts OrderedDict to dict
        self.resolve_path(endpoint_url)
        self.set_endpoint_path()

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

    def set_endpoint_path(self):
        """
        Sets endpoint path; the path we can use to index our OpenAPI schema, by using drf_yasg's path_prefix logic.

        Drf_yasg `cleans` schema paths by finding recurring path patterns, and cutting them out of the generated openapi schema.
        For example, /api/v1/... might then become /v1/...
        """
        self.endpoint_path = convert_resolved_url(self.resolved_route).replace(self.drf_yasg_path_prefix, '')

    def set_response_schema(self) -> None:
        """
        Indexes self.schema by url and HTTP method to assign self.response_schema.Z
        """
        # Index by route
        try:
            logger.debug('Indexing schema by route `%s`', self.endpoint_path)
            schema = self.schema['paths'][self.endpoint_path]
        except KeyError:
            raise SwaggerDocumentationError(
                f'Failed initialization\n\nError: Unsuccessfully tried to index the OpenAPI schema by '
                f'`{self.endpoint_path}`, but the key does not exist in the schema.'
                f'\n\nFor debugging purposes: valid urls include {", ".join([key for key in self.schema.keys()])}')

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

        self.response_schema = schema

    def _validate_response(self, response: Response, method: str, **kwargs) -> None:
        """
        This function verifies that an OpenAPI schema definition matches the an API response.
        It inspects the schema recursively, and verifies that the schema matches the structure of the response at every level.

        :param response: HTTP response
        :param method: HTTP method ('get', 'put', 'post', ...)
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
        """
        self.unpack_response(response)
        self.validate_method(method)
        self.set_ignored_keys(**kwargs)
        self.set_response_schema()
        if not self.response_schema:
            raise SwaggerDocumentationError('The OpenAPI schema is undefined. Schema is not testable.')

        if self.response_schema['type'] == 'object':
            self._dict(schema=self.response_schema, data=self.data, parent='root')
        elif self.response_schema['type'] == 'array':
            self._list(schema=self.response_schema, data=self.data, parent='root')
        elif self.response_schema['type'] in self._item_types():
            self._item(schema=self.response_schema, data=self.data, parent='root')
        else:
            raise Exception(f'Unexpected error.\nSchema: {self.response_schema}\nResponse: {self.data}\n\nThis shouldn\'t happen.')

    def _validate_input(self, serializer: Serializer, method: str, **kwargs) -> None:
        """
        This function verifies that an OpenAPI schema input definition is accepted by the endpoints serializer class.

        :param serializer: Serializer class
        :param method: HTTP method ('get', 'put', 'post', ...)
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
        """
        self.validate_method(method)
        self.set_ignored_keys(**kwargs)
        self.load_schema()  # <-- this method is extended from the base class; self.schema is defined here
        if not self.schema:
            raise SwaggerDocumentationError('The OpenAPI schema is undefined. Schema is not testable.')

        parameters = self.schema[self.endpoint_path][self.method]['parameters']
        for parameter in parameters:
            if '$ref' in parameter['schema']:
                input_example = self.schema['definitions'][parameter['schema']['$ref'].split('/')[-1]]['example']
            else:
                input_example = parameter['schema']['example']
            serializer = serializer(data=input_example)
            valid = serializer.is_valid()
            if not valid:
                raise SwaggerDocumentationError(f'Input example is not valid for endpoint {self.endpoint_path}')


def validate_response(response: Response, method: str, endpoint_url: str, **kwargs) -> None:
    """
    This function verifies that an OpenAPI schema definition matches the an API response.
    It inspects the schema recursively, and verifies that the schema matches the structure of the response at every level.

    :param response: HTTP response
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param endpoint_url: Relative path of the endpoint being tested
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
    """
    tester_class = DrfYasgSwaggerTester(endpoint_url=endpoint_url)
    tester_class._validate_response(response=response, method=method, **kwargs)


def validate_input(serializer: Serializer, method: str, endpoint_url: str) -> None:
    """

    :param serializer:
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param endpoint_url: Relative path of the endpoint being tested
    """
    tester_class = DrfYasgSwaggerTester(endpoint_url=endpoint_url)
    tester_class._validate_input(serializer=serializer, method=method)
