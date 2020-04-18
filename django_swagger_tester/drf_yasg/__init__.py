from rest_framework.response import Response
from rest_framework.serializers import Serializer

from django_swagger_tester.drf_yasg.loader import LoadDrfYasgSchema as loader_class
from django_swagger_tester.input_validation.validation import input_validation
from django_swagger_tester.response_validation.validation import response_validation


def validate_response(response: Response, method: str, route: str, **kwargs) -> None:
    """
    Verifies that an OpenAPI schema definition matches an API response.

    It inspects the schema recursively,
    and verifies that the schema matches the structure of the response at every level.

    :param response: HTTP response
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param route: Relative path of the endpoint being tested
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError or django_swagger_tester.exceptions.CaseError
    """
    return response_validation(loader_class=loader_class, response=response, method=method, route=route, **kwargs)


def validate_input(serializer: Serializer, method: str, route: str, **kwargs) -> None:
    """
    Verifies that an OpenAPI schema request body definition is valid, according to the API view's input serializer.

    :param serializer: Serializer class used for input validation in your API view
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param route: Relative path of the endpoint being tested
    :param camel_case_parser: True if request body should be camel cased - this is usually required when you're using
           djangorestframework-camel-case parses for your APIs.
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError or django_swagger_tester.exceptions.CaseError
    """
    return input_validation(loader_class=loader_class, serializer=serializer, method=method, route=route, **kwargs)
