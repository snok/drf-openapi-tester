import json
import logging

from rest_framework.response import Response

from django_swagger_tester.configuration import settings
from django_swagger_tester.exceptions import SwaggerDocumentationError, CaseError
from django_swagger_tester.schema_tester import SchemaTester
from django_swagger_tester.utils import format_response_tester_error, unpack_response, format_response_tester_case_error

logger = logging.getLogger('django_swagger_tester')


def validate_response(response: Response, method: str, route: str, **kwargs) -> None:
    """
    Verifies that an OpenAPI schema definition matches an API response.

    It inspects the schema recursively, and verifies that the schema matches the structure of the response at every level.

    :param response: HTTP response
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param route: Relative path of the endpoint being tested
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError or django_swagger_tester.exceptions.CaseError
    """
    data, status_code = unpack_response(response)
    response_schema = settings.LOADER_CLASS.get_response_schema_section(
        route=route, status_code=status_code, method=method
    )
    try:
        SchemaTester(schema=response_schema, data=data, case_tester=settings.CASE_TESTER, **kwargs)
    except SwaggerDocumentationError as e:
        verbose_error_message = format_response_tester_error(e)
        raise SwaggerDocumentationError(verbose_error_message)
    except CaseError as e:
        verbose_error_message = format_response_tester_case_error(e)
        raise SwaggerDocumentationError(verbose_error_message)


def validate_input_serializer(
    serializer, method: str, route: str, camel_case_parser: bool = settings.CAMEL_CASE_PARSER  # noqa: F401, TYP001
) -> None:
    """
    Verifies that an OpenAPI schema request body definition is valid, according to an API view's input serializer.

    :param serializer: Serializer class used for input validation in your API view
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param route: Relative path of the endpoint being tested
    :param camel_case_parser: True if request body should be camel cased - this is usually required when you're using
           djangorestframework-camel-case parses for your APIs.
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError or django_swagger_tester.exceptions.CaseError
    """
    example = settings.LOADER_CLASS.get_request_body_example(route, method)

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
