import logging
from functools import wraps
from typing import Callable

from django.core.exceptions import ImproperlyConfigured
from rest_framework.request import Request
from rest_framework.response import Response

from django_swagger_tester.configuration import settings
from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.schema_validation.request_body.validation import input_validation as _input_validation
from django_swagger_tester.schema_validation.response.validation import response_validation as _response_validation

logger = logging.getLogger('django_swagger_tester')


def validate_response_schema(response: Response, method: str, route: str, **kwargs) -> None:
    """
    Calls the response validation function with the static schema loader class.

    :param response: HTTP response
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param route: Relative path of the endpoint being tested
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError or django_swagger_tester.exceptions.CaseError
    """
    return _response_validation(
        loader_class=settings.SCHEMA_LOADER, response=response, method=method, route=route, **kwargs
    )


def validate_request_body_schema(
    serializer, method: str, route: str, camel_case_parser: bool = settings.CAMEL_CASE_PARSER, **kwargs  # noqa: TYP001
) -> None:
    """
    Calls the input validation function with the static schema loader class.

    :param serializer: Serializer class used for input validation in your API view
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param route: Relative path of the endpoint being tested
    :param camel_case_parser: True if request body should be camel cased - this is usually required when you're using
           djangorestframework-camel-case parses for your APIs.
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError or django_swagger_tester.exceptions.CaseError
    """
    return _input_validation(
        loader_class=settings.SCHEMA_LOADER,
        serializer=serializer,
        method=method,
        route=route,
        camel_case_parser=camel_case_parser,
        **kwargs,
    )


def validate(request_body=False, uri_parameter=False, response=False):
    def outer(fn: Callable):
        @wraps(fn)
        def inner(*args, **kwargs):
            if not isinstance(args[0], Request):
                raise ImproperlyConfigured('The first argument to a view needs to be a Request')

            if request_body:
                # input validation function here
                print('Request body', args[0].data)

            if uri_parameter:
                # path param validation function here
                print('URI parameters', kwargs)

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
