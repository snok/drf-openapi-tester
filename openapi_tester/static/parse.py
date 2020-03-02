import logging
from typing import Union

from django.urls import resolve
from django.urls.exceptions import Resolver404

logger = logging.getLogger('openapi_tester')


def parse_endpoint(schema: dict, method: str, endpoint_url: str, status_code: Union[int, str]) -> dict:
    """
    Returns the section of an OpenAPI schema we want to test, i.e., the 200 response.

    :param schema: OpenAPI specification, dict
    :param method: HTTP method, str
    :param endpoint_url: An endpoints' resolvable URL, str
    :param status_code: HTTP response code
    :return: dict
    """
    logger.debug(
        'Collecting %s %s section of the OpenAPI schema.',
        method.upper() if method else method,
        endpoint_url.lower() if endpoint_url else endpoint_url,
    )

    # Validate method
    methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']
    if not isinstance(method, str) or method.lower() not in methods:
        logger.error('Method `%s` is invalid. Should be one of: %s.', method, ', '.join([i.upper() for i in methods]))
        raise ValueError(f'Method `{method}` is invalid. Should be one of: {", ".join([i.upper() for i in methods])}.')

    # Resolve path/url
    try:
        logger.debug('Resolving path.')
        resolved_path = resolve(endpoint_url)
    except Resolver404:
        logger.error(f'URL `%s` is invalid. Hint: remember to use both leading and ending forward slashes.', endpoint_url)
        raise ValueError(f'Could not resolve path `{endpoint_url}`')

    # Match the path to an OpenAPI endpoint
    resolved_path.route = ('/' + resolved_path.route + '/').replace('//', '/')  # The schema has leading slashes, but resolved urls dont

    matching_endpoints = [endpoint for endpoint in [key for key in schema['paths']] if endpoint in resolved_path.route]
    if len(matching_endpoints) == 0:
        raise ValueError('Could not match the resolved url to a documented endpoint in the OpenAPI specification')
    else:
        matched_endpoint = matching_endpoints[0]

    # Return the 200 response schema of that endpoint
    if method.lower() in schema['paths'][matched_endpoint]:
        return schema['paths'][matched_endpoint][method.casefold()]['responses'][f'{status_code}']['content']['application/json']['schema']
    else:
        logger.error('Schema section for %s does not exist.', method)
        raise KeyError(f'The OpenAPI schema has no method called `{method}`')
