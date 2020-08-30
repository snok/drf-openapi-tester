import json
import logging
import os
from json import dumps, loads
from typing import Optional, Any

from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.exceptions import OpenAPISchemaError, UndocumentedSchemaSectionError
from django_swagger_tester.openapi import list_types, read_properties
from django.apps import apps

logger = logging.getLogger('django_swagger_tester')


class _LoaderBase:
    """
    Base class for OpenAPI schema loading classes.

    The base contains a template of methods that are required from a loader class.
    """

    def __init__(self) -> None:
        self.schema: Optional[dict] = None
        self.original_schema: Optional[dict] = None

    # < methods to be overwritten >

    def validation(self, *args, **kwargs) -> None:
        """
        This method should hold class level validation logic to be called in the subclass' init method.

        For example, useful validation could include checking for schema-type specific dependencies and configurations.
        """
        pass

    def load_schema(self) -> dict:
        """
        Loader function which must be overwritten by subclass.
        """
        raise ImproperlyConfigured('The `load_schema` method has to be overwritten.')

    # </ methods to be overwritten >

    def get_schema(self,) -> dict:
        """
        Returns the OpenAPI schema as a dict.
        """
        if self.schema is None:
            self.set_schema(self.load_schema())
        return self.schema  # type: ignore

    def set_schema(self, schema: dict,) -> None:
        """
        Sets self.schema as a cleaned version of the loaded schema
        """
        self.schema = self.replace_refs(schema,)
        self.original_schema = schema

    def get_route(self, route: str) -> str:
        """
        Returns the appropriate route.

        This method was primarily implemented because drf-yasg has its own route style.
        """
        from django_swagger_tester.utils import resolve_path

        return resolve_path(route)[0]

    def get_response_schema_section(self, route: str, method: str, status_code: int) -> dict:
        """
        Indexes schema by url, HTTP method, and status code to get the schema section related to a specific response.

        :param route: Schema-compatible path
        :param method: HTTP request method
        :param status_code: HTTP response code
        :return Response schema
        """
        from django_swagger_tester.openapi import index_schema

        self.validate_method(method)
        self.validate_route(route)
        self.validate_status_code(status_code)
        schema_route = self.get_route(route)
        schema = self.get_schema()

        # Index by paths
        paths_schema = index_schema(schema=schema, variable='paths')

        # Index by route
        routes = ', '.join([key for key in paths_schema.keys()])
        route_error = (
            f'\n\nFor debugging purposes: valid routes include {routes}.\n\nTo skip validation for this route '
            f'you can add `^{route}$` to the VALIDATION_EXEMPT_URLS setting list.'
        )
        route_schema = index_schema(schema=paths_schema, variable=schema_route, error_addon=route_error)

        # Index by method
        joined_methods = ', '.join([method.upper() for method in route_schema.keys() if method.upper() != 'PARAMETERS'])
        method_error = f'\n\nAvailable methods include {joined_methods}.'
        method_schema = index_schema(schema=route_schema, variable=method.lower(), error_addon=method_error)

        # Index by responses
        responses_schema = index_schema(schema=method_schema, variable='responses')

        # Index by status code
        status_code_error = (
            f'\n\nDocumented responses include(s) {", ".join([f"`{code}`" for code in responses_schema.keys()])}. '
            f'Is the `{status_code}` response documented?'
        )
        status_code_schema = index_schema(
            schema=responses_schema, variable=str(status_code), error_addon=status_code_error
        )

        # Not sure about this logic - this is what my static schema looks like, but not the drf_yasg dynamic schema
        if 'content' in status_code_schema and 'application/json' in status_code_schema['content']:
            status_code_schema = status_code_schema['content']['application/json']

        return index_schema(status_code_schema, 'schema')

    def get_request_body_schema_section(self, route: str, method: str,) -> dict:
        """
        Indexes schema to get an endpoints request body.

        :param method: HTTP request method
        :param route: Schema-compatible path
        :return: Request body schema
        """
        from django_swagger_tester.openapi import index_schema

        self.validate_method(method)
        self.validate_route(route)
        route = self.get_route(route)
        schema = self.get_schema()

        paths_schema = index_schema(schema=schema, variable='paths')
        route_error = (
            f'\n\nFor debugging purposes: valid routes include {", ".join([key for key in paths_schema.keys()])}'
        )
        route_schema = index_schema(schema=paths_schema, variable=route, error_addon=route_error)
        joined_methods = ', '.join([method.upper() for method in route_schema.keys() if method.upper() != 'PARAMETERS'])
        method_error = f'\n\nAvailable methods include {joined_methods}.'
        method_schema = index_schema(schema=route_schema, variable=method.lower(), error_addon=method_error)
        parameters_schema = index_schema(schema=method_schema, variable='parameters')
        try:
            parameter_schema = parameters_schema[0]
        except IndexError:
            raise OpenAPISchemaError(
                f'Request body does not seem to be documented. Schema parameters: {parameters_schema}'
            )
        if 'in' not in parameter_schema or parameter_schema['in'] != 'body':
            logger.debug('Request body schema seems to be missing a request body section')
            raise UndocumentedSchemaSectionError(
                'Tried to test request body documentation, but the provided schema has no request body.'
            )
        return parameter_schema['schema']

    @staticmethod
    def validate_route(route: str) -> None:
        """
        Validates a route.

        :param route: a django-resolved endpoint path
        :raises: ImproperlyConfigured
        """
        if not isinstance(route, str):
            raise ImproperlyConfigured('`route` is invalid.')

    @staticmethod
    def validate_method(method: str) -> str:
        """
        Validates a string as a HTTP method.

        :param method: HTTP method
        :raises: ImproperlyConfigured
        """
        methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']
        if not isinstance(method, str) or method.lower() not in methods:
            logger.error(
                'Method `%s` is invalid. Should be one of: %s.', method, ', '.join([i.upper() for i in methods])
            )
            raise ImproperlyConfigured(
                f'Method `{method}` is invalid. Should be one of: {", ".join([i.upper() for i in methods])}.'
            )
        return method

    @staticmethod
    def validate_status_code(status_code: int) -> None:
        """
        Validates a status code, if the status code is not None.

        :param status_code: the relevant HTTP response status code to check in the OpenAPI schema
        :raises: ImproperlyConfigured
        """
        if not isinstance(status_code, int):
            raise ImproperlyConfigured('`status_code` should be an integer.')
        if not 100 <= status_code <= 505:
            raise ImproperlyConfigured('`status_code` should be a valid HTTP response code.')

    @staticmethod
    def replace_refs(schema: dict,) -> dict:
        """
        Finds all $ref sections in a schema and replaces them with the referenced content.
        This way we only have to worry about $refs once.

        :param schema: OpenAPI schema
        :return Adjusted OpenAPI schema
        """
        if '$ref' not in str(schema):
            return schema

        def find_and_replace_refs_recursively(d: dict, s: dict) -> dict:
            """
            Iterates over a dictionary to look for pesky $refs.
            """
            if '$ref' in d:
                indices = [i for i in d['$ref'][d['$ref'].index('#') + 1 :].split('/') if i]
                temp_schema = s
                for index in indices:
                    logger.debug(f'Indexing schema by `%s`', index)
                    temp_schema = temp_schema[index]
                return temp_schema
            for k, v in d.items():
                if isinstance(v, list):
                    d[k] = iterate_list(v, s)
                elif isinstance(v, dict):
                    d[k] = find_and_replace_refs_recursively(v, s)
            return d

        def iterate_list(l: list, s: dict) -> list:
            """
            Loves to iterate lists.
            """
            x = []
            for i in l:
                if isinstance(i, list):
                    x.append(iterate_list(i, s))
                elif isinstance(i, dict):
                    x.append(find_and_replace_refs_recursively(i, s))  # type: ignore
                else:
                    x.append(i)
            return x

        return find_and_replace_refs_recursively(schema, schema)

    def get_request_body_example(self, route: str, method: str,) -> Any:
        logger.info('Fetching request body example for %s request to %s', method, route)
        request_body_schema = self.get_request_body_schema_section(route, method,)
        return request_body_schema.get('example', self.create_dict_from_schema(request_body_schema))

    def _iterate_schema_dict(self, d: dict) -> dict:
        from django_swagger_tester.openapi import read_type
        from django_swagger_tester.utils import type_placeholder_value

        x = {}
        for key, value in read_properties(d).items():
            if 'example' in value:
                x[key] = value['example']
            elif read_type(value) == 'object':
                x[key] = self._iterate_schema_dict(value)
            elif read_type(value) == 'array':
                x[key] = self._iterate_schema_list(value)  # type: ignore
            elif 'type' in value and value['type'] in list_types():
                logger.warning('Item `%s` is missing an explicit example value', value)
                x[key] = type_placeholder_value(value['type'])
            else:
                raise ImproperlyConfigured(f'This schema item does not seem to have an example value. Item: {value}')
        return x

    def _iterate_schema_list(self, l: dict) -> list:

        from django_swagger_tester.openapi import read_type, read_items
        from django_swagger_tester.utils import type_placeholder_value

        x = []
        i = read_items(l)
        if 'example' in i:
            x.append(i['example'])
        elif read_type(i) == 'object':
            x.append(self._iterate_schema_dict(i))
        elif read_type(i) == 'array':
            x.append(self._iterate_schema_list(i))  # type: ignore
        elif 'type' in i and i['type'] in list_types():
            logger.warning('Item `%s` is missing an explicit example value', i)
            x.append(type_placeholder_value(i['type']))
        else:
            raise ImproperlyConfigured(f'This schema item does not seem to have an example value. Item: {i}')
        return x

    def create_dict_from_schema(self, schema: dict) -> Any:
        """
        Converts an OpenAPI schema representation of a dict to dict.
        """
        from django_swagger_tester.openapi import read_type
        from django_swagger_tester.utils import type_placeholder_value

        if 'example' in schema:
            return schema['example']
        elif read_type(schema) == 'array' and schema['items']:
            logger.debug('--> list')
            return self._iterate_schema_list(schema)
        elif read_type(schema) == 'object':
            logger.debug('--> dict')
            return self._iterate_schema_dict(schema)
        elif 'type' in schema and schema['type'] in list_types():
            logger.warning('Item `%s` is missing an explicit example value', schema)
            return type_placeholder_value(schema['type'])
        else:
            raise ImproperlyConfigured(f'Not able to construct an example from schema {schema}')


class DrfYasgSchemaLoader(_LoaderBase):
    """
    Loads OpenAPI schema when schema is dynamically generated by drf_yasg.
    """

    def __init__(self,) -> None:
        super().__init__()
        self.validation()
        from drf_yasg.openapi import Info
        from drf_yasg.generators import OpenAPISchemaGenerator

        self.schema_generator = OpenAPISchemaGenerator(info=Info(title='', default_version=''))

    def validation(self, *args, **kwargs) -> None:
        """
        For drf_yasg-generated schemas, it's important that we verify:
        1. The package is installed
        2. drf_yasg is in the projects installed_apps
        """
        try:
            import drf_yasg  # noqa: F401
        except ModuleNotFoundError:
            raise ImproperlyConfigured(
                'The package `drf_yasg` is required. Please run `pip install drf_yasg` to install it.'
            )

        if 'drf_yasg' not in apps.app_configs.keys():
            raise ImproperlyConfigured(
                'The package `drf_yasg` is missing from INSTALLED_APPS. Please add it to your '
                '`settings.py`, as it is required for this implementation'
            )

    def load_schema(self,) -> dict:
        """
        Loads generated schema from drf-yasg and returns it as a dict.
        """
        odict_schema = self.schema_generator.get_schema(None, True)
        schema = loads(dumps(odict_schema.as_odict()))
        logger.debug('Successfully loaded schema')
        return schema

    def get_path_prefix(self) -> str:
        """
        Returns the drf_yasg specified path prefix.

        Drf_yasg `cleans` schema paths by finding recurring path patterns,
        and cutting them out of the generated openapi schema.
        For example, `/api/v1/example` might then just become `/example`
        """
        from django_swagger_tester.utils import get_endpoint_paths

        return self.schema_generator.determine_path_prefix(get_endpoint_paths())

    def get_route(self, route: str) -> str:
        """
        Returns a url that matches the urls found in a drf_yasg-generated schema.

        :param route: Django resolved route
        """
        from django_swagger_tester.utils import resolve_path

        resolved_route = resolve_path(route)[0]
        path_prefix = self.get_path_prefix()  # typically might be 'api/' or 'api/v1/'
        logger.debug('Path prefix: %s', path_prefix)
        if path_prefix != '/':
            return resolved_route[len(path_prefix) :]
        else:
            return resolved_route


class StaticSchemaLoader(_LoaderBase):
    """
    Loads OpenAPI schema from a static file.
    """

    def __init__(self,) -> None:
        super().__init__()
        self.path: str = ''

    def set_path(self, path: str) -> None:
        """
        Sets value for self.path
        """
        self.path = path

    def validation(self, *args, **kwargs) -> None:
        """
        Before trying to load static schema, we need to verify that:
        - The path to the static file is provided, and that the file type is compatible (json/yml/yaml)
        - The right parsing library is installed (pyYAML for yaml, json is builtin)
        """
        if (
            'package_settings' not in kwargs
            or 'PATH' not in kwargs['package_settings']
            or kwargs['package_settings']['PATH'] is None
        ):
            logger.error('PATH setting is not specified')
            raise ImproperlyConfigured(
                f'PATH is required to load static OpenAPI schemas. Please add PATH to the SWAGGER_TESTER settings.'
            )
        elif not isinstance(kwargs['package_settings']['PATH'], str):
            logger.error('PATH setting is not a string')
            raise ImproperlyConfigured('`PATH` needs to be a string. Please update your SWAGGER_TESTER settings.')
        if '.yml' in kwargs['package_settings']['PATH'] or '.yaml' in kwargs['package_settings']['PATH']:
            try:
                import yaml  # noqa: F401
            except ModuleNotFoundError:
                raise ImproperlyConfigured(
                    'The package `PyYAML` is required for parsing yaml files. '
                    'Please run `pip install PyYAML` to install it.'
                )
        self.set_path(kwargs['package_settings']['PATH'])

    def load_schema(self) -> dict:
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
            schema = json.loads(content)
            logger.debug('Successfully loaded schema')
            return schema
        elif '.yaml' in self.path or '.yml' in self.path:
            import yaml

            schema = yaml.load(content, Loader=yaml.FullLoader)
            logger.debug('Successfully loaded schema')
            return schema
        else:
            raise ImproperlyConfigured('The specified file path does not seem to point to a JSON or YAML file.')
