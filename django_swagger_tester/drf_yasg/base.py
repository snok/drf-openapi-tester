import json
import logging

from requests import Response
from rest_framework.serializers import Serializer

from django_swagger_tester.case.base import ResponseCaseTester, ResponseSchemaCaseTester
from django_swagger_tester.drf_yasg.load_schema import LoadDrfYasgSchema
from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.input_validation.utils import serialize_request_body_schema
from django_swagger_tester.response_validation.base import ResponseTester
from django_swagger_tester.utils import unpack_response

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
    loader = LoadDrfYasgSchema(route=route, status_code=status_code, method=method)
    response_schema = loader.get_response_schema()
    ResponseTester(response_schema=response_schema, response_data=data)
    ResponseCaseTester(response_data=data, **kwargs)
    ResponseSchemaCaseTester(schema=response_schema, **kwargs)


def validate_input(serializer: Serializer, method: str, route: str, camel_case_parser: bool = False) -> None:
    """
    Verifies that an OpenAPI schema request body definition is valid, according to the API view's input serializer.

    :param serializer: Serializer class used for input validation in your API view
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param route: Relative path of the endpoint being tested
    :param camel_case_parser: True if request body should be camel cased - this is usually required when you're using
        djangorestframework-camel-case parses for your APIs.
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError or django_swagger_tester.exceptions.CaseError
    """
    loader = LoadDrfYasgSchema(route=route, method=method)
    request_body_schema = loader.get_request_body()
    json_request_body = serialize_request_body_schema(request_body_schema)
    if camel_case_parser:
        from djangorestframework_camel_case.util import underscoreize

        json_request_body = underscoreize(json_request_body)
    serializer = serializer(data=json_request_body)  # type: ignore
    if not serializer.is_valid():
        raise SwaggerDocumentationError(
            f'Request body is not valid according to the passed serializer.'
            f'\n\nSwagger example request body: \n\n\t{json.dumps(json_request_body)}'
            f'\n\nSerializer error:\n\n\t{json.dumps(serializer.errors)}'
        )
