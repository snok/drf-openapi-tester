import json
import logging
from copy import deepcopy
from re import compile
from typing import Callable, Union

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.urls import Resolver404
from rest_framework.response import Response

from django_swagger_tester.configuration import settings
from django_swagger_tester.exceptions import (
    CaseError,
    SwaggerDocumentationError,
    UndocumentedSchemaSectionError,
)
from django_swagger_tester.utils import Route, format_response_tester_error, get_endpoint_paths, resolve_path

logger = logging.getLogger('django_swagger_tester')


class ResponseValidationMiddleware(object):
    """
    Middleware validates incoming request bodies and outgoing responses with respect to the app's OpenAPI schema.
    """

    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        self.endpoints = get_endpoint_paths()
        self.middleware_settings = settings.RESPONSE_VALIDATION_MIDDLEWARE
        self.exempt_urls = [compile(url_pattern) for url_pattern in self.middleware_settings.VALIDATION_EXEMPT_URLS]

        # This logic cannot be moved to configuration.py because apps are not yet initialized when that is executed
        if not apps.is_installed('django_swagger_tester'):
            raise ImproperlyConfigured('django_swagger_tester must be listed in your installed apps')

    def __call__(self, request: HttpRequest) -> Union[HttpRequest, HttpResponse]:
        """
        Validates API requests not listed in VALIDATION_EXEMPT_URLS.

        Can validate request body, response data, or both, depending on settings and the type of request.
        """
        method = request.method
        path = request.path

        # we skip validation if the route is ignored in the settings
        if any(m.match(request.path_info.lstrip('/')) for m in self.exempt_urls):
            logger.debug('Validation skipped: %s request to `%s` is in VALIDATION_EXEMPT_URLS', method, path)
            return self.get_response(request)
        # ..or if the request path doesn't point to a valid endpoint
        elif not self.path_in_endpoints(path=path, method=method):
            # note: this covers both non-endpoint routes, and any route that doesn't resolve
            logger.debug('Validation skipped: `%s` is not a relevant endpoint', path)
            return self.get_response(request)

        # -- ^ Code above this line is executed before the view and later middleware --
        response = self.get_response(request)

        # -- Response validation --
        if response.get('Content-Type', '') == 'application/json':
            logger.debug('Validating response')
            # By parsing the response data JSON we bypass problems like uuid's not having been converted to
            # strings yet, which otherwise would create problems when comparing response data types to the
            # documented schema types in the schema tester
            content = response.content.decode(response.charset)
            response_data = json.loads(content)
            copied_response = deepcopy(response)
            copied_response.data = response_data  # this can probably be done differently
            self.validate_response(copied_response, request)
        else:
            logger.debug('Validation skipped - response for %s request to %s has non-JSON content-type', method, path)

        return response

    def validate_response(self, response: Response, request: HttpRequest) -> None:
        """
        Validates an outgoing response object against the OpenAPI schema response documentation.

        In case of inconsistencies, a log is logged at a setting-specified log level.

        :param response: HTTP response
        :param request: HTTP request
        """
        logger.info('Validating response for %s request to %s', request.method, request.path)

        try:
            # load the response schema
            response_schema = settings.LOADER_CLASS.get_response_schema_section(
                route=request.path,
                status_code=response.status_code,
                method=request.method,
                skip_validation_warning=True,
            )
        except UndocumentedSchemaSectionError as e:
            self.middleware_settings.LOGGER(
                'Failed accessing response schema for %s request to `%s`. Error: %s', request.method, request.path, e
            )
            return

        try:
            # validate response data with respect to response schema
            from django_swagger_tester.schema_tester import SchemaTester

            SchemaTester(
                schema=response_schema,
                data=response.data,
                case_tester=settings.CASE_TESTER,
                camel_case_parser=settings.CAMEL_CASE_PARSER,
                origin='response',
            )
            logger.info('Response valid for %s request to %s', request.method, request.path)
        except SwaggerDocumentationError as e:
            long_message = format_response_tester_error(e, hint=e.response_hint, addon='')
            self.middleware_settings.LOGGER(
                'Bad response returned for %s request to %s. Error: %s', request.method, request.path, str(long_message)
            )
        except CaseError as e:
            self.middleware_settings.LOGGER('Found incorrectly cased cased key, `%s` in %s', e.key, e.origin)

    def path_in_endpoints(self, path: str, method: str) -> bool:
        """
        Indicates whether a path belongs in an OpenAPI schema or not.

        We're only interested in validating requests meant for documented API endpoints.

        :param path: the request path
        :param method: the request method
        :return: boolean indicating whether the request should be handled or not
        """
        try:
            route_object = Route(*resolve_path(path))
        except ValueError:
            logger.debug('Validation skipped - %s request to %s failed to resolve', method, path)
            return False
        except Resolver404:
            logger.debug('Validation skipped - %s request to %s failed to resolve', method, path)
            return False

        for route in self.endpoints:
            if (
                route_object.route_matches(route)
                and hasattr(route_object.resolved_path, 'func')
                and hasattr(route_object.resolved_path.func, 'view_class')
            ):
                # Verify that the view has contains the method
                if hasattr(route_object.resolved_path.func.view_class, method.lower()):
                    logger.debug('%s request to %s is an API request', method, path)
                    return True
                else:
                    logger.debug('%s request method does not exist in the view class', method)
        logger.debug('Validation skipped - %s request to %s was not found in API endpoints', method, path)
        return False
