import json
import logging
from functools import wraps
from typing import Callable

from django.core.exceptions import ImproperlyConfigured
from rest_framework.request import Request
from rest_framework.response import Response

from django_swagger_tester.configuration import settings
from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.schema_validation.case import ResponseCaseTester
from django_swagger_tester.schema_validation.case import SchemaCaseTester
from django_swagger_tester.schema_validation.schema_tester import SchemaTester
from django_swagger_tester.schema_validation.utils import unpack_response

logger = logging.getLogger('django_swagger_tester')


def validate_response_schema(response: Response, method: str, route: str, **kwargs) -> None:
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
    SchemaTester(response_schema=response_schema, response_data=data, **kwargs)
    ResponseCaseTester(response_data=data, **kwargs)
    SchemaCaseTester(schema=response_schema, **kwargs)


def drf_serializer_validate_request_body_schema(
    serializer, method: str, route: str, camel_case_parser: bool = settings.CAMEL_CASE_PARSER, **kwargs
) -> None:
    """
    Verifies that an OpenAPI schema request body definition is valid, according to the API view's input serializer.

    :param serializer: Serializer class used for input validation in your API view
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param route: Relative path of the endpoint being tested
    :param camel_case_parser: True if request body should be camel cased - this is usually required when you're using
           djangorestframework-camel-case parses for your APIs.
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError or django_swagger_tester.exceptions.CaseError
    """
    request_body_schema = settings.LOADER_CLASS.get_request_body_schema_section(route, method)
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

    # Check the example's case for inconsistencies
    SchemaCaseTester(request_body_schema, **kwargs)


def validate(request_body=False, response=False, **kwargs):
    """
    Wrapper function to enable middleware-style validation, but for individual API views.

    :param request_body: Whether to validate the request body
    :param response: Whether to validate the response
    """

    def outer(fn: Callable):
        @wraps(fn)
        def inner(*args, **kwargs):
            if not isinstance(args[0], Request):
                raise ImproperlyConfigured('The first argument to a view needs to be a Request')

            if request_body:
                # input validation function here
                print('Request body', args[0].data)

            # ^ Code above this line happens before the view is run
            output = fn(*args, **kwargs)

            if response:
                # response validation function here
                try:
                    validate_response_schema(response=output, method=args[0].method.upper(), route=args[0].path)
                except SwaggerDocumentationError as e:
                    logger.error(
                        'Response from <class name> (<route>) returned an incorrect response, '
                        'with respect to the OpenAPI schema'
                    )

            return output

        return inner

    return outer
