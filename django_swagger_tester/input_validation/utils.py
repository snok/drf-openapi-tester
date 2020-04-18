import logging

from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.openapi import index_schema
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
    schema = replace_refs(schema)
    no_ref_schema = replace_refs(schema)
    paths_schema = index_schema(schema=no_ref_schema, variable='paths')
    route_error = f'\n\nFor debugging purposes: valid routes include {", ".join([key for key in paths_schema.keys()])}'
    route_schema = index_schema(schema=paths_schema, variable=route, error_addon=route_error)
    method_error = f'\n\nAvailable methods include {", ".join([method.upper() for method in route_schema.keys() if method.upper() != "PARAMETERS"])}.'
    method_schema = index_schema(schema=route_schema, variable=method.lower(), error_addon=method_error)
    return index_schema(schema=method_schema, variable='parameters')


def serialize_request_body_schema(request_body_schema: dict) -> dict:
    """
    Translates the `parameters` section of an OpenAPI schema to an example request body.

    :param request_body_schema: Schema section
    :return: Example request body
    """
    schema = request_body_schema[0]
    if 'in' not in schema or schema['in'] != 'body':
        raise ImproperlyConfigured('Input validation tries to test request body documentation, '
                                   'but the provided schema has no request body.')
    return schema['schema']['example']
