import difflib
import logging
from typing import List, Tuple, Optional

from django.core.exceptions import ImproperlyConfigured
from django.urls import Resolver404, resolve
from requests import Response
from rest_framework.schemas.generators import EndpointEnumerator

logger = logging.getLogger('django_swagger_tester')


def get_paths() -> List[str]:
    """
    Returns a list of endpoint paths.
    """
    return list(set(endpoint[0] for endpoint in EndpointEnumerator().get_api_endpoints()))  # noqa: C401


def resolve_path(endpoint_path: str) -> str:
    """
    Resolves a Django path.
    """
    try:
        logger.debug('Resolving path.')
        if endpoint_path == '' or endpoint_path[0] != '/':
            logger.debug('Adding leading `/` to provided path')
            endpoint_path = '/' + endpoint_path
        try:
            resolved_route = resolve(endpoint_path)
            logger.debug('Resolved %s successfully', endpoint_path)
        except Resolver404:
            resolved_route = resolve(endpoint_path + '/')
            endpoint_path = (
                endpoint_path + '/'
            )  # if we don't change endpoint path here, indexing paths will fail later on
            logger.warning('Endpoint path is missing a trailing slash: %s', endpoint_path)

        kwarg = resolved_route.kwargs
        for key, value in kwarg.items():
            # Replacing kwarg values back into the string seems to be the simplest way of bypassing complex regex handling
            # However, its important not to freely use the .replace() function, as a {value} of `1` would also cause the `1` in api/v1/ to
            # be replaced
            var_index = endpoint_path.rfind(value)
            endpoint_path = endpoint_path[:var_index] + f'{{{key}}}' + endpoint_path[var_index + len(value) :]
        return endpoint_path

    except Resolver404:
        logger.error(f'URL `%s` did not resolve successfully', endpoint_path)
        paths = get_paths()
        closest_matches = ''.join([f'\n- {i}' for i in difflib.get_close_matches(endpoint_path, paths)])
        if closest_matches:
            raise ValueError(
                f'Could not resolve path `{endpoint_path}`.\n\nDid you mean one of these?{closest_matches}\n\n'
                f'If your path contains path parameters (e.g., `/api/<version>/...`), make sure to pass a '
                f'value, and not the parameter pattern.'
            )
        raise ValueError(f'Could not resolve path `{endpoint_path}`')


def validate_method(method: str) -> str:
    """
    Validates a string as a HTTP method.
    """
    methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']
    if not isinstance(method, str) or method.lower() not in methods:
        logger.error('Method `%s` is invalid. Should be one of: %s.', method, ', '.join([i.upper() for i in methods]))
        raise ImproperlyConfigured(
            f'Method `{method}` is invalid. Should be one of: {", ".join([i.upper() for i in methods])}.'
        )
    return method


def unpack_response(response: Response) -> Tuple[dict, int]:
    """
    Unpacks HTTP response.
    """
    try:
        status_code = response.status_code
    except Exception as e:
        logger.exception('Unable to open response object')
        raise ValueError(
            f'Unable to unpack response object. Make sure you are passing response, and not response.json(). Error: {e}'
        )
    if hasattr(response, 'json'):
        return response.json(), status_code
    else:
        raise ImproperlyConfigured(
            'Response does not contain a JSON-formatted response and cannot be tested against a response schema.'
        )


def replace_refs(schema: dict) -> dict:
    """
    Finds all $ref sections in a schema and replaces them with the referenced content.
    This way we only have to worry about $refs once.

    :param schema: OpenAPI schema
    :return Adjusted OpenAPI schema
    """
    if '$ref' not in str(schema):
        return schema

    def find_and_replace_refs_recursively(d: dict, schema: dict) -> dict:
        """
        Iterates over a dictionary to look for pesky $refs.
        """
        if '$ref' in d:
            indices = [i for i in d['$ref'][d['$ref'].index('#') + 1 :].split('/') if i]
            temp_schema = schema
            for index in indices:
                logger.debug(f'indexing by %s', index)
                temp_schema = temp_schema[index]
            return temp_schema
        for k, v in d.items():
            if isinstance(v, list):
                d[k] = iterate_list(v, schema)
            elif isinstance(v, dict):
                d[k] = find_and_replace_refs_recursively(v, schema)
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


def validate_inputs(route: str, status_code: Optional[int], method: str) -> None:
    """
    Input validation for response validator classes.

    :param route: a django-resolved endpoint path
    :param status_code: the relevant HTTP response status code to check in the OpenAPI schema
    :param method: the relevant HTTP method to check in the OpenAPI schema
    :raises: ImproperlyConfigured
    """
    if not isinstance(route, str):
        raise ImproperlyConfigured('`route` is invalid.')
    validate_method(method)
    if status_code is not None:
        if not isinstance(status_code, int):
            raise ImproperlyConfigured('`status_code` should be an integer.')
        if not 100 <= status_code <= 505:
            raise ImproperlyConfigured('`status_code` should be a valid HTTP response code.')
