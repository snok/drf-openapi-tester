import json
import logging

import yaml
from requests.exceptions import ConnectionError

from openapi_tester.exceptions import ImproperlyConfigured

logger = logging.getLogger('openapi-tester')


def authenticated_client():  # noqa: TYP201
    """
    Get valid user and attach credentials to client

    :return: APIClient
    """
    from rest_framework.test import APIClient
    from django.contrib.auth.models import User

    logger.debug('Authenticating API client.')
    user, _ = User.objects.update_or_create(username='test_user')
    client: APIClient = APIClient()
    client.force_authenticate(user=user)
    return client


def fetch_from_url(url: str) -> dict:
    """
    Fetches OpenAPI specification from URL.

    :param url: str
    :return: dict
    """
    try:
        client = authenticated_client()
        logger.debug('Fetching OpenAPI schema from %s', url)
        response = client.get(url, format='json')
    except ConnectionError as e:
        logger.exception('ConnectionError raised when fetching OpenAPI schema from %s.', url)
        raise ConnectionError(
            f'\n\nNot able to connect to the specified openapi url. Please make sure the specified path is correct.\n\nError: {e}'
        )
    if 400 <= response.status_code <= 600:
        logger.exception('Received bad response when fetching OpenAPI schema from %s. Response code: %s.', url, response.status_code)
        raise ImproperlyConfigured(
            '\n\nCould not fetch the OpenAPI specification. Please make sure your documentation is '
            f'set to public and that the path specified is correct.\n\nAPI response code: {response.status_code}'
        )
    return response.json()


def fetch_from_dir(path: str) -> dict:
    """
    Fetches json or yaml contents from a file.

    :param path: str
    :return: dict
    :raises: ImproperlyConfigured
    """
    try:
        logger.debug('Fetching OpenAPI schema from %s', path)
        with open(path, 'r') as f:
            content = f.read()
    except Exception as e:
        logger.exception('Exception raised when fetching OpenAPI schema from %s. Error: %s.', path, e)
        raise ImproperlyConfigured(
            f'\n\nCould not read the openapi specification. Please make sure the path setting is correct.\n\nError: {e}'
        )
    if '.json' in path:
        return json.loads(content)
    elif '.yaml' in path or '.yml' in path:
        return yaml.load(content, Loader=yaml.FullLoader)
    else:
        raise ImproperlyConfigured('The specified file path does not seem to point to a JSON or YAML file.')


def fetch_specification(path: str, is_url: bool) -> dict:
    """
    Fetches the hosted OpenAPI specification using the DRF APIClient.

    :param path: The path to the specification, str
    :param is_url: Indicates whether the path is an url, bool
    :return: OpenAPI specification, dict
    """
    if is_url:
        return fetch_from_url(path)
    else:
        return fetch_from_dir(path)
