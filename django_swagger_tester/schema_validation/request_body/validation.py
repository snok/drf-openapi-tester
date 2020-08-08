import json
import logging

from django_swagger_tester.configuration import settings
from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.schema_validation.case.base import SchemaCaseTester
from django_swagger_tester.schema_validation.request_body.utils import get_request_body_schema_section, serialize_schema

logger = logging.getLogger('django_swagger_tester')


def get_request_body_schema(route, method):
    endpoint_schema = settings.LOADER_CLASS.get_request_body(route=route, method=method)
    return get_request_body_schema_section(endpoint_schema)


def get_request_body_example(request_body_schema: dict):
    return request_body_schema.get('example', serialize_schema(request_body_schema))


# noinspection PyUnboundLocalVariable
def input_validation(serializer, method: str, route: str, camel_case_parser: bool, **kwargs,) -> None:  # noqa: TYP001
    """
    Verifies that an OpenAPI schema request body definition is valid, according to the API view's input serializer.

    :param serializer: Serializer class used for input validation in your API view
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param route: Relative path of the endpoint being tested
    :param camel_case_parser: True if request body should be camel cased - this is usually required when you're using
           djangorestframework-camel-case parses for your APIs.
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError or django_swagger_tester.exceptions.CaseError
    """
    request_body_schema = get_request_body_schema(route, method)
    example = get_request_body_example(request_body_schema)

    # Make camelCased input snake_cased so the serializer can read it
    if camel_case_parser:
        from djangorestframework_camel_case.util import underscoreize

        example = underscoreize(example)

    logger.debug('Validating example: %s', example)
    serializer = serializer(data=example)  # type: ignore
    if not serializer.is_valid():
        logger.info('Example was invalid')
        raise SwaggerDocumentationError(
            f'Request body is not valid according to the passed serializer.'
            f'\n\nSwagger example request body: \n\n\t{json.dumps(example)}'
            f'\n\nSerializer error:\n\n\t{json.dumps(serializer.errors)}\n\n'
            f'Note: If all your parameters are correct, you might need to change `camel_case_parser` to True or False.'
        )

    # Check the example's case for inconsistencies
    SchemaCaseTester(request_body_schema, **kwargs)
