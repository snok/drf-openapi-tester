import json
import logging

from rest_framework.serializers import Serializer

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.input_validation.utils import serialize_request_body_schema

logger = logging.getLogger('django_swagger_tester')


def input_validation(
    loader_class,  # noqa: TYP001
    serializer: Serializer,
    method: str,
    route: str,
    camel_case_parser: bool = False,
    **kwargs,
) -> None:
    """
    Verifies that an OpenAPI schema request body definition is valid, according to the API view's input serializer.

    :param loader_class: Class containing a `get_request_body` method
    :param serializer: Serializer class used for input validation in your API view
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param route: Relative path of the endpoint being tested
    :param camel_case_parser: True if request body should be camel cased - this is usually required when you're using
           djangorestframework-camel-case parses for your APIs.
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError or django_swagger_tester.exceptions.CaseError
    """
    loader = loader_class(route=route, method=method, **kwargs)
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
    # TODO: Write a request body case tester to run after validation
