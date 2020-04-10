import difflib
import logging
import re
from typing import List, Tuple

from django.urls import Resolver404, resolve
from requests import Response
from rest_framework.schemas.generators import EndpointEnumerator

logger = logging.getLogger('django_swagger_tester')


def get_paths() -> List[str]:
    """
    Returns a list of endpoint paths.
    """
    return list(set(endpoint[0] for endpoint in EndpointEnumerator().get_api_endpoints()))  # noqa: C401


def convert_resolved_url(resolved_url: str) -> str:
    """
    Converts an url:

        - from /api/v1/<vehicle_type:vehicle_type>/ to /api/v1/{vehicle_type}/, and
        - from /api/v1/<vehicle_type>/ to /api/v1/{vehicle_type}/

    :return: Converted url
    """
    patterns = [
        {
            'pattern': r'<\w+:\w+>',
            'string_pattern': '<{keyword}:{keyword}>',
            'first_index': '<',
            'second_index': ':'
        },
        {
            'pattern': r'<\w+>',
            'string_pattern': '<{keyword}>',
            'first_index': '<',
            'second_index': '>'
        }]

    for item in patterns:
        matches = re.findall(item['pattern'], resolved_url)
        if matches:
            url = resolved_url
            for dynamic_url in matches:
                keyword = dynamic_url[dynamic_url.index(item['first_index']) + 1: dynamic_url.index(item['second_index'])]
                url = url.replace(item['string_pattern'].format(keyword=keyword), f'{{{keyword}}}')
            logger.debug('Converted resolved url from `%s` to `%s`', resolved_url, url)
            resolved_url = url
    return resolved_url





def resolve_path(endpoint_path: str) -> None:
    """
    Resolves a Django path.
    """
    try:
        logger.debug('Resolving path.')
        if endpoint_path[0] != '/':
            logger.debug('Adding leading `/` to provided path')
            endpoint_path = '/' + endpoint_path
        try:
            resolved_route = '/' + resolve(endpoint_path).route.replace('$', '')
            logger.debug('Resolved %s successfully', endpoint_path)
            return resolved_route
        except Resolver404:
            resolved_route = '/' + resolve(endpoint_path + '/').route
            logger.warning('Endpoint path is missing a trailing slash (`/`)', endpoint_path)
            return resolved_route
    except Resolver404:
        logger.error(f'URL `%s` did not resolve succesfully', endpoint_path)
        paths = get_paths()
        closest_matches = ''.join([f'\n- {i}' for i in difflib.get_close_matches(endpoint_path, paths)])
        if closest_matches:
            raise ValueError(f'Could not resolve path `{endpoint_path}`.\n\nDid you mean one of these?{closest_matches}\n\n'
                             f'If your path contains path parameters (e.g., `/api/<version>/...`), make sure to pass a '
                             f'value, and not the parameter pattern.')
        else:
            raise ValueError(f'Could not resolve path `{endpoint_path}`')


def validate_method(method: str) -> bool:
    """
    Validates a string as a HTTP method.
    """
    methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']
    if not isinstance(method, str) or method.lower() not in methods:
        logger.error('Method `%s` is invalid. Should be one of: %s.', method, ', '.join([i.upper() for i in methods]))
        raise ValueError(f'Method `{method}` is invalid. Should be one of: {", ".join([i.upper() for i in methods])}.')
    return True


def unpack_response(response: Response) -> Tuple[dict, int]:
    """
    Unpacks HTTP response.
    """
    try:
        return response.json(), response.status_code
    except Exception as e:
        logger.exception('Unable to open response object')
        raise ValueError(f'Unable to unpack response object. Make sure you are passing response, and not response.json(). Error: {e}')


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
            indeces = [i for i in d['$ref'][d['$ref'].index('#') + 1:].split('/') if i]
            temp_schema = schema
            for index in indeces:
                logger.debug(f'indexing by %s', index)
                temp_schema = temp_schema[index]
            return temp_schema
        for k, v in d.items():
            if isinstance(v, list):
                d[k] = iterate_list(v, schema)
            elif isinstance(v, dict):
                d[k] = find_and_replace_refs_recursively(v, schema)
        return d

    def iterate_list(l: list, schema: dict) -> list:
        """
        Loves to iterate lists.
        """
        x = []
        for i in l:
            if isinstance(i, list):
                x.append(iterate_list(i, schema))
            elif isinstance(i, dict):
                x.append(find_and_replace_refs_recursively(i, schema))  # type: ignore
            else:
                x.append(i)
        return x

    return find_and_replace_refs_recursively(schema, schema)
