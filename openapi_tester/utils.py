import re

from django.urls import resolve
from django.urls.exceptions import Resolver404


def snake_case(string: str) -> str:
    """
    Converts an input string to snake_case.

    :param string: str
    :return: str
    """
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)).lower()


def camel_case(string: str) -> str:
    """
    Converts an input string to camelCase.

    :param string: str
    :return: str
    """
    string = re.sub(r'^[\-_.]', '', str(string))
    if not string:
        return string
    return string[0].lower() + re.sub(r'[\-_.\s]([a-z])', lambda matched: matched.group(1).upper(), string[1:])


def parse_endpoint(schema: dict, method: str, path: str) -> dict:
    """
    Returns the section of an OpenAPI schema we want to test, i.e., the 200 response.

    :param schema: OpenAPI specification, dict
    :param method: HTTP method, str
    :param path: An endpoints' resolvable URL, str
    :return: dict
    """
    # Validate method
    methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']
    if method.lower() not in methods:
        raise ValueError(f'Invalid value for `method`. Needs to be one of: {", ".join([i.upper() for i in methods])}.')

    # Resolve path/url
    try:
        resolved_path = resolve(path)
    except Resolver404:
        raise ValueError(f'Could not resolve path `{path}`')

    # Match the path to an OpenAPI endpoint
    matching_endpoints = [endpoint for endpoint in [key for key in schema['paths']] if endpoint in resolved_path.route]
    if len(matching_endpoints) == 0:
        raise ValueError('Could not match the resolved url to a documented endpoint in the OpenAPI specification')
    elif len(matching_endpoints) == 1:
        matched_endpoint = matching_endpoints[0]
    else:
        # We probably shouldn't ever let this happen
        # TODO: Try to make it happen in testing, and work out a better way to do this
        raise ValueError('Matched the resolved urls to too many endpoints.')

    # Return the 200 response schema of that endpoint
    return schema['paths'][matched_endpoint][method.casefold()]['responses']['200']['schema']
