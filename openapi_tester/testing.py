import logging
from typing import Any

from django.core.exceptions import ImproperlyConfigured
from rest_framework.test import APITestCase

import openapi_tester.type_declarations as td
from openapi_tester.configuration import settings
from openapi_tester.exceptions import CaseError, DocumentationError
from openapi_tester.schema_tester import SchemaTester
from openapi_tester.utils import format_error, format_openapi_tester_case_error, unpack_response

logger = logging.getLogger('openapi_tester')


def validate_response(response: td.Response, method: str, route: str, **kwargs) -> None:
    """
    Verifies that an OpenAPI schema definition matches an API response.

    It inspects the schema recursively, and verifies that the schema matches the structure of the response at every level.

    :param response: The HTTP response
    :param method: The HTTP method ('get', 'put', 'post', ...)
    :param route: The relative path of the endpoint which sent the response (must be resolvable)
    :keyword ignore_case: List of strings to ignore when testing the case of response keys
    :keyword camel_case_parser: Boolean to indicate whether djangorestframework-camel-case parsers are active for this endpoint
    :raises: ``openapi_tester.exceptions.DocumentationError`` if we find inconsistencies in the API response and schema.

             ``openapi_tester.exceptions.CaseError`` if we find case errors.
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
        verbose_error_message = format_error(e, hint=e.response_hint)
        raise DocumentationError(verbose_error_message)
    except CaseError as e:
        verbose_error_message = format_openapi_tester_case_error(e)
        raise DocumentationError(verbose_error_message)


class OpenAPITestCase(APITestCase):
    """
    Extends APITestCase with OpenAPI assertions.
    """

    # noinspection PyPep8Naming
    def assertResponse(self, response: td.Response, **kwargs: Any) -> None:
        """
        Assert response matches the OpenAPI spec.
        """
        route = kwargs.pop('route', response.request['PATH_INFO'])
        method = kwargs.pop('method', response.request['REQUEST_METHOD'])
        try:
            validate_response(response=response, method=method, route=route, **kwargs)
        except (DocumentationError, CaseError) as e:
            raise self.failureException from e
