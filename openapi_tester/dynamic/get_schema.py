import logging
from collections import OrderedDict
from json import dumps, loads

from openapi_tester.exceptions import SpecificationError

logger = logging.getLogger('openapi_tester')


def ordered_dict_to_dict(d: OrderedDict) -> dict:
    """
    Converts a nested OrderedDict to dict.
    """
    return loads(dumps(d))


def fetch_generated_schema(url: str, method: str) -> dict:
    """
    Fetches dynamically generated schema.

    :param url: API endpoint URL, str
    :param method: HTTP method, str
    :return: dict
    """
    logger.debug('Fetching generated dynamic schema')
    from drf_yasg.openapi import Info
    from drf_yasg.generators import OpenAPISchemaGenerator

    schema = OpenAPISchemaGenerator(info=Info(title='', default_version='')).get_schema()
    schema = ordered_dict_to_dict(schema.as_odict())['paths']
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
            raise SpecificationError('Both 200 and 201 are documented, but they should be mutually exclusive')
        else:
            raise SpecificationError('200 and 201 response codes are undocumented in the schema.')
    except KeyError:
        raise KeyError(
            f'No schema found for response code 200. Documented responses include '
            f'{", ".join([code for code in schema.keys() if code != "200"])}.'
        )
