import logging

logger = logging.getLogger('openapi-tester')


def fetch_generated_schema(url: str, status_code: str, method: str) -> dict:
    """
    Fetches OpenAPI specification from URL.

    :param url: str
    :return: dict
    """
    from drf_yasg.openapi import Info
    from drf_yasg.generators import OpenAPISchemaGenerator

    return OpenAPISchemaGenerator(info=Info(title='test', default_version='test')).get_schema()['paths'][url][method.lower()]['responses'][
        status_code
    ]
