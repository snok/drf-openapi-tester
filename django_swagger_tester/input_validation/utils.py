import logging
from typing import Union

from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.exceptions import OpenAPISchemaError
from django_swagger_tester.openapi import index_schema, read_items, read_type
from django_swagger_tester.utils import replace_refs

logger = logging.getLogger('django_swagger_tester')


def get_request_body(schema: dict, method: str, route: str) -> dict:
    """
    Indexes schema to get an endpoints request body.

    :param schema: Full OpenAPI schema
    :param method: HTTP request method
    :param route: Schema-compatible path
    :return: Request body schema
    """
    no_ref_schema = replace_refs(schema)
    paths_schema = index_schema(schema=no_ref_schema, variable='paths')
    route_error = f'\n\nFor debugging purposes: valid routes include {", ".join([key for key in paths_schema.keys()])}'
    route_schema = index_schema(schema=paths_schema, variable=route, error_addon=route_error)
    joined_methods = ', '.join([method.upper() for method in route_schema.keys() if method.upper() != 'PARAMETERS'])
    method_error = f'\n\nAvailable methods include {joined_methods}.'
    method_schema = index_schema(schema=route_schema, variable=method.lower(), error_addon=method_error)
    return index_schema(schema=method_schema, variable='parameters')


def get_request_body_schema(request_body_schema: dict) -> dict:
    """
    Translates the `parameters` section of an OpenAPI schema to an example request body.

    :param request_body_schema: Schema section
    :return: Example request body
    """
    try:
        schema = request_body_schema[0]
    except IndexError:
        raise OpenAPISchemaError(
            f'Request body does not seem to be documented. Schema parameters: {request_body_schema}'
        )
    if 'in' not in schema or schema['in'] != 'body':
        logger.debug('Request body schema seems to be missing a request body section')
        raise ImproperlyConfigured(
            'Tried to test request body documentation, but the provided schema has no request body.'
        )
    return schema['schema']


def _iterate_schema_dict(d: dict) -> dict:
    x = {}
    for key, value in d['properties'].items():
        if read_type(value) == 'object':
            x[key] = _iterate_schema_dict(value)
        elif read_type(value) == 'array':
            x[key] = _iterate_schema_list(value)  # type: ignore
        elif 'example' in value:
            x[key] = value['example']
        else:
            raise ImproperlyConfigured(f'This schema item does not seem to have an example value. Item: {value}')
    return x


def _iterate_schema_list(l: dict) -> list:
    x = []
    i = read_items(l)
    if read_type(i) == 'object':
        x.append(_iterate_schema_dict(i))
    elif read_type(i) == 'array':
        x.append(_iterate_schema_list(i))  # type: ignore
    elif 'example' in i:
        x.append(i['example'])
    else:
        raise ImproperlyConfigured(f'This schema item does not seem to have an example value. Item: {i}')
    return x


def serialize_schema(schema: dict) -> Union[list, dict, str, int, bool]:
    """
    Converts an OpenAPI schema representation of a dict to dict.
    """
    if read_type(schema) == 'array':
        logger.debug('--> list')
        return _iterate_schema_list(schema)
    elif read_type(schema) == 'object':
        logger.debug('--> dict')
        return _iterate_schema_dict(schema)
    elif 'example' in schema:
        return schema['example']
    else:
        raise ImproperlyConfigured(f'This schema item does not seem to have an example value. Item: {schema}')
