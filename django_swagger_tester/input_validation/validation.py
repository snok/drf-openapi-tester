import json
import logging

from django_swagger_tester.case.base import SchemaCaseTester
from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.input_validation.utils import get_request_body_schema, serialize_schema

logger = logging.getLogger('django_swagger_tester')


# noinspection PyUnboundLocalVariable
def input_validation(
    loader_class,  # noqa: TYP001
    serializer,  # noqa: TYP001
    method: str,
    route: str,
    camel_case_parser: bool,
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
    endpoint_schema = loader.get_request_body()

    request_body_schema = get_request_body_schema(endpoint_schema)
    if 'example' in request_body_schema:
        # Find a ready dict object
        # This happens when you use your Serializer as the request body parameter in drf_yasg auto schemas
        example = request_body_schema['example']
    else:
        # Parses schema bit by bit
        # This happens if you use static schemas or document your request body using Schema objects in drf_yasg
        example = serialize_schema(request_body_schema)

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
