import json
import logging
import os.path

import yaml
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger('django_swagger_tester')


def fetch_from_dir(path: str) -> dict:
    """
    Fetches OpenAPI json or yaml contents from a static file.

    :param path: str
    :return: dict
    :raises: ImproperlyConfigured
    """
    if not os.path.isfile(path):
        logger.error('Path `%s` does not resolve as a valid file.', path)
        raise ImproperlyConfigured(
            f'The path `{path}` does not point to a valid file. Make sure to point to the specification file.')

    try:
        logger.debug('Fetching static OpenAPI schema from %s', path)
        with open(path, 'r') as f:
            content = f.read()
    except Exception as e:
        logger.exception('Exception raised when fetching OpenAPI schema from %s. Error: %s.', path, e)
        raise ImproperlyConfigured(
            f'Could not read the openapi specification. Please make sure the path setting is correct.\n\nError: {e}')

    if '.json' in path:
        return json.loads(content)
    elif '.yaml' in path or '.yml' in path:
        return yaml.load(content, Loader=yaml.FullLoader)
    else:
        raise ImproperlyConfigured('The specified file path does not seem to point to a JSON or YAML file.')
