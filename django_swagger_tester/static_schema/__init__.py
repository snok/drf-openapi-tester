from rest_framework.response import Response

from django_swagger_tester.configuration import settings
from django_swagger_tester.input_validation.validation import input_validation as _input_validation
from django_swagger_tester.response_validation.validation import response_validation as _response_validation
from django_swagger_tester.static_schema.loader import LoadStaticSchema as _loader_class


def validate_response(response: Response, method: str, route: str, **kwargs) -> None:
    """
    Calls the response validation function with the static schema loader class.

    :param response: HTTP response
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param route: Relative path of the endpoint being tested
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError or django_swagger_tester.exceptions.CaseError
    """
    return _response_validation(loader_class=_loader_class, response=response, method=method, route=route, **kwargs)


def validate_input(
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
        loader_class=_loader_class,
        serializer=serializer,
        method=method,
        route=route,
        camel_case_parser=camel_case_parser,
        **kwargs,
    )
