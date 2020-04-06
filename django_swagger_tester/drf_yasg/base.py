import logging

from requests import Response
from rest_framework.serializers import Serializer

from django_swagger_tester.case.base import CaseTester
from django_swagger_tester.drf_yasg.load_schema import LoadDrfYasgSchema
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
    loader = LoadDrfYasgSchema(route=route, status_code=response.status_code, method=method)
    response_schema = loader.get_response_schema()
    ResponseTester(response_schema=response_schema, response_data=data)
    CaseTester(**kwargs)

def validate_input(serializer: Serializer, method: str, route: str) -> None:
    """
    Verifies that an OpenAPI schema request body definition is valid, according to the API view's input serializer.

    :param serializer: Serializer class used for input validation in your API view
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param route: Relative path of the endpoint being tested
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError or django_swagger_tester.exceptions.CaseError
    """
    # TODO: Finish rewrite
    # tester_class = DrfYasgSwaggerTester(endpoint_url=endpoint_url)
    # tester_class._validate_input(serializer=serializer, method=method)
    pass
#
# def _validate_input(self, serializer: Serializer, method: str, **kwargs) -> None:
#     """
#     This function verifies that an OpenAPI schema input definition is accepted by the endpoints serializer class.
#
#     :param serializer: Serializer class
#     :param method: HTTP method ('get', 'put', 'post', ...)
#     :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
#     """
#     self.validate_method(method)
#     self.set_ignored_keys(**kwargs)
#     self.load_schema()  # <-- this method is extended from the base class; self.schema is defined here
#     if not self.schema:
#         raise SwaggerDocumentationError('The OpenAPI schema is undefined. Schema is not testable.')
#
#     parameters = self.schema[self.endpoint_path][self.method]['parameters']
#     for parameter in parameters:
#         if '$ref' in parameter['schema']:
#             input_example = self.schema['definitions'][parameter['schema']['$ref'].split('/')[-1]]['example']
#         else:
#             input_example = parameter['schema']['example']
#         serializer = serializer(data=input_example)
#         valid = serializer.is_valid()
#         if not valid:
#             raise SwaggerDocumentationError(f'Input example is not valid for endpoint {self.endpoint_path}')
