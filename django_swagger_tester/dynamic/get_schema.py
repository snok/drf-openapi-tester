import logging
from json import dumps, loads
from typing import Union

from django_swagger_tester.exceptions import OpenAPISchemaError

logger = logging.getLogger('django_swagger_tester')


def fetch_generated_schema(url: str, method: str, status_code: Union[int, str]) -> dict:
    """
    Fetches a dynamically generated OpenAPI schema.

    :param url: API endpoint URL, str
    :param method: HTTP method, str
    :param status_code: HTTP response code
    :return: The section of the schema relevant for testing, dict
    """
    logger.debug('Fetching generated dynamic schema')
    from drf_yasg.openapi import Info
    from drf_yasg.generators import OpenAPISchemaGenerator

    # Fetch schema and convert to dict
    schema = OpenAPISchemaGenerator(info=Info(title='', default_version='')).get_schema()
    schema = loads(dumps(schema.as_odict()['paths']))  # Converts OrderedDict to dict

    try:
        schema = schema[url]
    except KeyError:
        raise OpenAPISchemaError(
            f'No path found for url `{url}`. Valid urls include {", ".join([key for key in schema.keys()])}')

    try:
        schema = schema[method.lower()]['responses']
    except KeyError:
        raise OpenAPISchemaError(
            f'No schema found for method {method.upper()}. Available methods include '
            f'{", ".join([method.upper() for method in schema.keys() if method.upper() != "PARAMETERS"])}.'
        )

    try:
        schema = schema[f'{status_code}']['schema']
    except KeyError:
        raise OpenAPISchemaError(
            f'No schema found for response code {status_code}. Documented responses include '
            f'{", ".join([code for code in schema.keys()])}.'
        )

    return schema
