import logging

logger = logging.getLogger('openapi_tester')


def fetch_generated_schema(url: str, status_code: str, method: str) -> dict:
    """
    Fetches dynamically generated schema.

    :param url: API endpoint URL, str
    :param status_code: Response status code, str
    :param method: HTTP method, str
    :return: dict
    """
    logger.debug('Returning generate dyanmic schema')
    from drf_yasg.openapi import Info
    from drf_yasg.generators import OpenAPISchemaGenerator

    return OpenAPISchemaGenerator(info=Info(title='test', default_version='test')).get_schema()['paths'][url][method.lower()]['responses'][
        status_code
    ]
