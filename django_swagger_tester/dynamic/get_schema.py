import logging
from json import dumps, loads

from django_swagger_tester.exceptions import OpenAPISchemaError

logger = logging.getLogger('django_swagger_tester')


def fetch_generated_schema(url: str, method: str) -> dict:
    """
    Fetches a dynamically generated OpenAPI schema.

    :param url: API endpoint URL, str
    :param method: HTTP method, str
    :return: The section of the schema relevant for testing, dict
    """
    logger.debug('Fetching generated dynamic schema')
    from drf_yasg.openapi import Info
    from drf_yasg.generators import OpenAPISchemaGenerator

    schema = OpenAPISchemaGenerator(info=Info(title='', default_version='')).get_schema()
    schema = loads(dumps(schema.as_odict()['paths']))  # Converts OrderedDict to dict
    try:
        schema = schema[url]
    except KeyError:
        raise KeyError(f'No path found for url `{url}`. Valid urls include {", ".join([key for key in schema.keys()])}')
    try:
        schema = schema[method.lower()]['responses']
    except KeyError:
        raise KeyError(
            f'No schema found for method {method.upper()}. Available methods include '
            f'{", ".join([method.upper() for method in schema.keys() if method.upper() != "PARAMETERS"])}.'
        )
    try:
        if '200' in schema and '201' not in schema:
            return schema['200']['schema']
        elif '201' in schema and '200' not in schema:
            return schema['201']['schema']
        elif '201' in schema and '200' in schema:
            raise OpenAPISchemaError('Both 200 and 201 are documented, but they should be mutually exclusive')
        else:
            raise OpenAPISchemaError('200 and 201 response codes are undocumented in the schema.')
    except KeyError:
        raise KeyError(
            f'No schema found for response code 200. Documented responses include '
            f'{", ".join([code for code in schema.keys() if code != "200"])}.'
        )
