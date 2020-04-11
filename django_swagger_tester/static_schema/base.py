from requests import Response

from django_swagger_tester.case.base import ResponseCaseTester, ResponseSchemaCaseTester
from django_swagger_tester.response_validation.base import ResponseTester
from django_swagger_tester.static_schema.load_schema import LoadStaticSchema
from django_swagger_tester.utils import unpack_response


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
    loader = LoadStaticSchema(route=route, status_code=response.status_code, method=method)
    response_schema = loader.get_response_schema()
    ResponseTester(response_schema=response_schema, response_data=data)
    ResponseCaseTester(response_data=data, **kwargs)
    ResponseSchemaCaseTester(schema=response_schema, **kwargs)
