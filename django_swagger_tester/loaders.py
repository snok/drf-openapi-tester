import json
import logging
import os
from json import dumps, loads
from typing import Any, Dict, Optional, Union

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.configuration import settings
from django_swagger_tester.exceptions import UndocumentedSchemaSectionError
from django_swagger_tester.openapi import list_types, read_properties
from django_swagger_tester.utils import Route

logger = logging.getLogger('django_swagger_tester')


class _LoaderBase:
    """
    Base class for OpenAPI schema loading classes.

    Contains a template of methods that are required from a loader class, and a range of helper methods for interacting
    with an OpenAPI schema.
    """

    def __init__(self) -> None:
        self.schema: Optional[dict] = None
        self.original_schema: Optional[dict] = None

    # < methods to be overwritten >

    def validation(self, *args, **kwargs) -> None:
        """
        Put class level validation logic here.

        For example, if you have specific dependencies for your loader class, you might want to check they're installed here.
        """
        pass

    def load_schema(self) -> dict:
        """
        Put logic required to load a schema and return it here.
        """
        raise ImproperlyConfigured('The `load_schema` method has to be overwritten.')

    # </ methods to be overwritten >

    def get_schema(self) -> dict:
        """
        Returns OpenAPI schema.
        """
        if self.schema is None:
            self.set_schema(self.load_schema())
        return self.schema  # type: ignore

    def set_schema(self, schema: dict) -> None:
        """
        Sets self.schema and self.original_schema.
        """
        self.schema = self.replace_refs(schema, loader=self)
        self.original_schema = schema

    def get_route(self, route: str) -> Route:
        """
        Returns the appropriate endpoint route.

        This method was primarily implemented because drf-yasg has its own route style, and so this method
        lets loader classes overwrite and add custom route conversion logic if required.
        """
        from django_swagger_tester.utils import resolve_path

        return Route(*resolve_path(route))

    def get_response_schema_section(self, route: str, method: str, status_code: Union[int, str], **kwargs) -> dict:
        """
        Indexes schema by url, HTTP method, and status code to get the schema section related to a specific response.

        :param route: Schema-compatible path
        :param method: HTTP request method
        :param status_code: HTTP response code
        :return Response schema
        """
        from django_swagger_tester.openapi import index_schema

        self.validate_method(method)
        self.validate_string(route, 'route')
        self.validate_status_code(status_code)
        route_object = self.get_route(route)
        schema = self.get_schema()

        # Index by paths
        paths_schema = index_schema(schema=schema, variable='paths')

        # Index by route
        routes = ', '.join(list(paths_schema))
        route_error = ''
        if routes:
            pretty_routes = '\n\t• '.join(routes.split())

            if settings.parameterized_i18n_name:
                route_error += (
                    '\n\nDid you specify the correct i18n parameter name? '
                    f'Your project settings specify `{settings.parameterized_i18n_name}` '
                    f'as the name of your parameterized language, meaning a path like `/api/en/items` '
                    f'will be indexed as `/api/{{{settings.parameterized_i18n_name}}}/items`.'
                )
            route_error += f'\n\nFor debugging purposes, other valid routes include: \n\n\t• {pretty_routes}'

        if 'skip_validation_warning' in kwargs and kwargs['skip_validation_warning']:
            route_error += (
                f'\n\nTo skip validation for this route you can add `^{route}$` '
                f'to your VALIDATION_EXEMPT_URLS setting list in your SWAGGER_TESTER.MIDDLEWARE settings.'
            )

        error = None
        for _ in range(len(route_object.parameters) + 1):
            try:
                # This is an unfortunate piece of logic, where we're attempting to insert path parameters
                # one by one until the path works
                # if it never works, we finally raise an UndocumentedSchemaSectionError
                route_schema = index_schema(
                    schema=paths_schema, variable=route_object.get_path(), error_addon=route_error
                )
                break
            except UndocumentedSchemaSectionError as e:
                error = e
            except IndexError:
                raise error  # type: ignore
        else:
            raise error  # type: ignore

        # Index by method
        joined_methods = ', '.join(method.upper() for method in route_schema.keys() if method.upper() != 'PARAMETERS')

        method_error = ''
        if joined_methods:
            method_error += f'\n\nAvailable methods include: {joined_methods}.'
        method_schema = index_schema(schema=route_schema, variable=method.lower(), error_addon=method_error)

        # Index by responses
        responses_schema = index_schema(schema=method_schema, variable='responses')

        # Index by status code
        responses = ', '.join(f'{code}' for code in responses_schema.keys())
        status_code_error = f' Is the `{status_code}` response documented?'
        if responses:
            status_code_error = f'\n\nDocumented responses include: {responses}. ' + status_code_error  # reverse add
        status_code_schema = index_schema(
            schema=responses_schema, variable=str(status_code), error_addon=status_code_error
        )

        # Not sure about this logic - this is what my static schema looks like, but not the drf_yasg dynamic schema
        if 'content' in status_code_schema and 'application/json' in status_code_schema['content']:
            status_code_schema = status_code_schema['content']['application/json']

        return index_schema(status_code_schema, 'schema')

    def get_request_body_schema_section(self, route: str, method: str) -> dict:
        """
        Indexes schema to get an endpoints request body.

        :param method: HTTP request method
        :param route: Schema-compatible path
        :return: Request body schema
        """
        from django_swagger_tester.openapi import index_schema

        self.validate_method(method)
        self.validate_string(route, 'route')
        route = self.get_route(route).get_path()
        schema = self.get_schema()

        paths_schema = index_schema(schema=schema, variable='paths')

        # Index by route
        routes = ', '.join(list(paths_schema))
        route_error = ''
        if routes:
            pretty_routes = '\n\t• '.join(routes.split())

            if settings.parameterized_i18n_name:
                route_error += (
                    '\n\nDid you specify the correct i18n parameter name? '
                    f'Your project settings specify `{settings.parameterized_i18n_name}` '
                    f'as the name of your parameterized language, meaning a path like `/api/en/items` '
                    f'will be indexed as `/api/{{{settings.parameterized_i18n_name}}}/items`.'
                )
            route_error += f'\n\nFor debugging purposes, other valid routes include: \n\n\t• {pretty_routes}'
        route_schema = index_schema(schema=paths_schema, variable=route, error_addon=route_error)

        # Index by method
        joined_methods = ', '.join(method.upper() for method in route_schema.keys() if method.upper() != 'PARAMETERS')

        method_error = ''
        if joined_methods:
            method_error += f'\n\nAvailable methods include: {joined_methods}.'
        method_schema = index_schema(schema=route_schema, variable=method.lower(), error_addon=method_error)

        parameters_schema = index_schema(schema=method_schema, variable='parameters')
        try:
            parameter_schema = parameters_schema[0]
        except IndexError:
            raise UndocumentedSchemaSectionError(
                f'Request body does not seem to be documented. `Parameters` is empty for path `{route}` and method `{method}`'
            )
        if 'in' not in parameter_schema or parameter_schema['in'] != 'body':
            logger.debug('Request body schema seems to be missing a request body section')
            raise UndocumentedSchemaSectionError(
                f'There is no in-body request body documented for route `{route}` and method `{method}`.'
            )
        return parameter_schema['schema']

    @staticmethod
    def validate_string(string: str, name: str) -> None:
        """
        Validates input as a string.
        """
        if not isinstance(string, str):
            raise ImproperlyConfigured(f'`{name}` is invalid.')

    @staticmethod
    def validate_method(method: str) -> str:
        """
        Validates a string as an HTTP method.

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
    def validate_status_code(status_code: Union[int, str]) -> None:
        """
        Validates a string or int as a valid HTTP response status code.

        :param status_code: the relevant HTTP response status code to check in the OpenAPI schema
        :raises: ImproperlyConfigured
        """
        try:
            status_code = int(status_code)
        except Exception:
            raise ImproperlyConfigured('`status_code` should be an integer.')
        if not 100 <= status_code <= 505:
            raise ImproperlyConfigured('`status_code` should be a valid HTTP response code.')

    @staticmethod
    def replace_refs(schema: dict, loader=None) -> dict:
        """
        Finds all schema references ($ref sections) in an OpenAPI schema and inserts them back into in place of the refs.
        This way we don't have to handle reference section when interacting with a loaded schema.

        * This does add a performance overhead to interacting with a schema, so changing this in the future would be fine *

        :param schema: OpenAPI schema
        :param loader: Current loader
        :return Adjusted OpenAPI schema
        """
        if '$ref' not in str(schema):
            return schema

        schemas_cache: Dict[str, dict] = {}

        def find_and_replace_refs_recursively(d: dict, s: dict) -> dict:
            """
            Iterates over a dictionary to look for pesky $refs.
            """
            if '$ref' in d:
                index_file, _, index_path = d['$ref'].partition('#')
                # index_path looks like `/GoodTrucksList`
                # index_file looks like `openapi-schema-split-datastructures.yaml` and will
                # be blank unless the openapi schema is split into several sections
                temp_schema: dict
                if not index_file:
                    # If index-file is empty, use local
                    temp_schema = s
                elif loader:
                    # If index-file is provided, look in the cache
                    full_path = os.path.join(os.path.dirname(loader.path), index_file)
                    schema_from_cache: Optional[dict] = schemas_cache.get(full_path)
                    if schema_from_cache is not None:
                        temp_schema = schema_from_cache
                    else:
                        # If we cannot find our reference in the cache load external defs
                        external_loader = loader.__class__()
                        external_loader.set_path(full_path)
                        temp_schema = external_loader.get_schema()
                        schemas_cache[full_path] = temp_schema
                else:
                    raise RuntimeError('loader is required for external references')

                indices = [i for i in index_path.split('/') if i]
                for index in indices:
                    logger.debug('Indexing schema by `%s`', index)
                    temp_schema = temp_schema[index]
                return temp_schema
            for k, v in d.items():
                if isinstance(v, list):
                    d[k] = iterate_list(v, s)
                elif isinstance(v, dict):
                    d[k] = find_and_replace_refs_recursively(v, s)
            return d

        def iterate_list(l: list, s: dict) -> list:  # noqa: E741
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

    def get_request_body_example(self, route: str, method: str) -> Any:
        """
        Returns a request body example.

        Does this either by returning a ready example from the schema, or by constructing an example manually.
        """
        logger.info('Fetching request body example for %s request to %s', method, route)
        request_body_schema = self.get_request_body_schema_section(route, method)
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
            else:
                logger.warning('Item `%s` is missing an explicit example value', value)
                x[key] = type_placeholder_value(value['type'])
        return x

    def _iterate_schema_list(self, l: dict) -> list:  # noqa: E741

        from django_swagger_tester.openapi import read_items, read_type
        from django_swagger_tester.utils import type_placeholder_value

        x = []
        i = read_items(l)
        if 'example' in i:
            x.append(i['example'])
        elif read_type(i) == 'object':
            x.append(self._iterate_schema_dict(i))
        elif read_type(i) == 'array':
            x.append(self._iterate_schema_list(i))  # type: ignore
        else:
            logger.warning('Item `%s` is missing an explicit example value', i)
            x.append(type_placeholder_value(i['type']))
        return x

    def create_dict_from_schema(self, schema: dict) -> Any:
        """
        Converts an OpenAPI schema representation of a dict to dict.
        """
        from django_swagger_tester.openapi import read_type
        from django_swagger_tester.utils import type_placeholder_value

        if 'example' in schema:
            return schema['example']
        elif read_type(schema) == 'array' and 'items' in schema and schema['items']:
            logger.debug('--> list')
            return self._iterate_schema_list(schema)
        elif read_type(schema) == 'object' and 'properties' in schema or 'additionalProperties' in schema:
            logger.debug('--> dict')
            return self._iterate_schema_dict(schema)
        elif 'type' in schema and schema['type'] in list_types(cut=['object', 'array']):
            logger.warning('Item `%s` is missing an explicit example value', schema)
            return type_placeholder_value(schema['type'])
        else:
            raise ImproperlyConfigured(f'Not able to construct an example from schema {schema}')


class DrfYasgSchemaLoader(_LoaderBase):
    """
    Loads OpenAPI schema generated by drf_yasg.
    """

    def __init__(self) -> None:
        super().__init__()
        self.validation()  # this has to run before drf_yasg imports
        from drf_yasg.generators import OpenAPISchemaGenerator
        from drf_yasg.openapi import Info

        logger.debug('Initialized drf-yasg loader schema')

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

    def load_schema(self) -> dict:
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

    def get_route(self, route: str) -> Route:
        """
        Returns a url that matches the urls found in a drf_yasg-generated schema.

        :param route: Django resolved route
        """
        from django_swagger_tester.utils import resolve_path

        deparameterized_path, resolved_path = resolve_path(route)
        path_prefix = self.get_path_prefix()  # typically might be 'api/' or 'api/v1/'
        if path_prefix == '/':
            path_prefix = ''
        logger.debug('Path prefix: %s', path_prefix)
        return Route(deparameterized_path=deparameterized_path[len(path_prefix) :], resolved_path=resolved_path)


class DrfSpectacularSchemaLoader(_LoaderBase):
    """
    Loads OpenAPI schema generated by drf_spectacular.
    """

    def __init__(self) -> None:
        super().__init__()
        self.validation()  # this has to run before drf_spectacular imports
        from drf_spectacular.generators import SchemaGenerator

        self.schema_generator = SchemaGenerator()
        logger.debug('Initialized drf-spectacular loader schema')

    def validation(self, *args, **kwargs) -> None:
        """
        For drf_spectacular-generated schemas, it's important that we verify:
        1. The package is installed
        2. drf_spectacular is in the projects installed_apps
        """
        try:
            import drf_spectacular  # noqa: F401
        except ModuleNotFoundError:
            raise ImproperlyConfigured(
                'The package `drf_spectacular` is required. Please run `pip install drf_spectacular` to install it.'
            )

        if 'drf_spectacular' not in apps.app_configs.keys():
            raise ImproperlyConfigured(
                'The package `drf_spectacular` is missing from INSTALLED_APPS. Please add it to your '
                '`settings.py`, as it is required for this implementation'
            )

    def load_schema(self) -> dict:
        """
        Loads generated schema from drf_spectacular and returns it as a dict.
        """
        return loads(dumps(self.schema_generator.get_schema(None, True)))

    def get_path_prefix(self) -> str:
        """
        Returns the drf_spectacular specified path prefix.
        """
        from drf_spectacular.settings import spectacular_settings

        return spectacular_settings.SCHEMA_PATH_PREFIX

    def get_route(self, route: str) -> Route:
        """
        Returns a url that matches the urls found in a drf_spectacular-generated schema.

        :param route: Django resolved route
        """
        from django_swagger_tester.utils import resolve_path

        deparameterized_path, resolved_path = resolve_path(route)
        path_prefix = self.get_path_prefix()  # typically might be 'api/' or 'api/v1/'
        if path_prefix == '/':
            path_prefix = ''
        logger.debug('Path prefix: %s', path_prefix)
        return Route(deparameterized_path=deparameterized_path[len(path_prefix) :], resolved_path=resolved_path)


class StaticSchemaLoader(_LoaderBase):
    """
    Loads OpenAPI schema from a static file.
    """

    def __init__(self) -> None:
        super().__init__()
        self.path: str = ''
        logger.debug('Initialized static loader schema')

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
                'PATH is required to load static OpenAPI schemas. Please add PATH to the SWAGGER_TESTER settings.'
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
            with open(self.path) as f:
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
