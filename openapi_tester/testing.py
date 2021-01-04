import logging
from typing import TYPE_CHECKING, Any

from openapi_tester.configuration import settings
from openapi_tester.exceptions import CaseError, DocumentationError
from openapi_tester.schema_tester import SchemaTester
from openapi_tester.utils import format_response_tester_case_error, format_response_tester_error, unpack_response

logger = logging.getLogger('openapi_tester')

if TYPE_CHECKING:
    try:
        from rest_framework.response import Response
    except ImportError:
        from django.http.response import HttpResponse as Response

try:
    from rest_framework.test import APITestCase
except ImportError:
    pass


def validate_response(response: 'Response', method: str, route: str, **kwargs) -> None:
    """
    Verifies that an OpenAPI schema definition matches an API response.

    It inspects the schema recursively, and verifies that the schema matches the structure of the response at every level.

    :param response: HTTP response
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param route: Relative path of the endpoint being tested
    :raises: openapi_tester.exceptions.DocumentationError or openapi_tester.exceptions.CaseError
    """
    data, status_code = unpack_response(response)
    response_schema = settings.loader_class.get_response_schema_section(
        route=route, status_code=status_code, method=method
    )
    try:
        SchemaTester(
            schema=response_schema,
            data=data,
            case_tester=settings.case_tester,
            camel_case_parser=settings.camel_case_parser,
            origin='response',
            **kwargs,
        )
    except DocumentationError as e:
        verbose_error_message = format_response_tester_error(e, hint=e.response_hint)
        raise DocumentationError(verbose_error_message)
    except CaseError as e:
        verbose_error_message = format_response_tester_case_error(e)
        raise DocumentationError(verbose_error_message)


class OpenAPITestCase(APITestCase):
    """
    Extends APITestCase with OpenAPI assertions.
    """

    def assertResponse(self, response: 'Response', **kwargs: Any) -> None:
        """
        Assert response matches the OpenAPI spec.
        """
        route = kwargs.pop('route', response.request['PATH_INFO'])
        method = kwargs.pop('method', response.request['REQUEST_METHOD'])
        try:
            validate_response(response=response, method=method, route=route, **kwargs)
        except (DocumentationError, CaseError) as e:
            raise self.failureException from e
