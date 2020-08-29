import json
import logging
from copy import deepcopy
from json import JSONDecodeError
from re import compile
from typing import Callable, Optional, Union

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.urls import Resolver404
from rest_framework.response import Response

from django_swagger_tester.configuration import settings
from django_swagger_tester.exceptions import (
    CaseError,
    OpenAPISchemaError,
    SwaggerDocumentationError,
    UndocumentedSchemaSectionError,
)
from django_swagger_tester.schema_tester import SchemaTester
from django_swagger_tester.utils import format_response_tester_error, get_endpoint_paths, resolve_path

logger = logging.getLogger('django_swagger_tester')


class SwaggerValidationMiddleware(object):
    """
    Middleware validates incoming request bodies and outgoing responses with respect to the apps OpenAPI schema.

    With the default settings, an invalid schema, response, or request body, will log a message
    at a setting-specified log level (the default log level is error).

    If specified, the request body validation will reject invalid requests, returning a 400-response
    with a description of what triggered the rejection.
    """

    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        self.endpoints = get_endpoint_paths()
        self.middleware_settings = settings.MIDDLEWARE
        self.exempt_urls = [compile(url_pattern) for url_pattern in self.middleware_settings.VALIDATION_EXEMPT_URLS]

        # This logic cannot be moved to configuration.py because apps are not yet initialized when that is executed
        if not apps.is_installed('django_swagger_tester'):
            raise ImproperlyConfigured('django_swagger_tester must be listed in your installed apps')

    def __call__(self, request: HttpRequest) -> Union[HttpRequest, HttpResponse]:
        """
        Contains the middleware flow.
        """
        # Skip validation if the route is ignored in the settings
        if any(m.match(request.path_info.lstrip('/')) for m in self.exempt_urls):
            logger.debug('Validation skipped - %s request to %s is in exempt urls', request.method, request.path)
            return self.get_response(request)

        # Skip validation if the request path is not a valid endpoint
        elif not self.path_in_endpoints(path=request.path, method=request.method):
            return self.get_response(request)

        # Code below this line is handled by the middleware

        if request.body and self.middleware_settings.VALIDATE_REQUEST_BODY:
            # Skip validation if the request has a non-JSON content type
            # - support for other content types could be added in the future
            if request.headers['Content-Type'] != 'application/json':
                logger.debug(
                    'Validation skipped - %s request to %s has non-JSON content-type', request.method, request.path
                )
            else:
                logger.debug('Validating request body')
                potential_response = self.validate_request_body(
                    request, strict=self.middleware_settings.REJECT_INVALID_REQUEST_BODIES
                )
                # If validation function rejects the request, we return a 400 - only if strict is True
                if potential_response is not None:
                    return potential_response

        # ^ Code above this line is executed before the view and later middleware
        response = self.get_response(request)

        if self.middleware_settings.VALIDATE_RESPONSE:
            content_type = response.get('Content-Type', '')
            if content_type == 'application/json':
                logger.debug('Validating response')
                # By parsing the response data JSON we bypass problems like uuid's not having been converted to
                # strings, which creates problems when comparing response data types to the documented schema types
                # in the schema tester
                content = response.content.decode(response.charset)
                response_data = json.loads(content)
                copied_response = deepcopy(response)
                copied_response.data = response_data
                self.validate_response(copied_response, request)
            else:
                logger.debug(
                    'Validation skipped - response for %s request to %s has non-JSON content-type',
                    request.method,
                    request.path,
                )
        return response

    def validate_response(self, response: Response, request: HttpRequest) -> None:
        """
        Validates an outgoing response object against the OpenAPI schema response documentation.

        In case of inconsistencies, a log is logged at a setting-specified log level.

        :param response: HTTP response
        :param request: HTTP request
        """
        logger.info('Validating response for %s request to %s', request.method, request.path)

        # Get the section of the schema relevant for this request
        try:
            response_schema = settings.LOADER_CLASS.get_response_schema_section(
                route=request.path, status_code=response.status_code, method=request.method
            )
        except UndocumentedSchemaSectionError as e:
            self.middleware_settings.LOGGER(
                'Failed accessing schema section for %s request to `%s`. Error: %s', request.method, request.path, e
            )
            return

        # Validate response against schema
        try:
            SchemaTester(
                schema=response_schema,
                data=response.data,
                case_tester=settings.CASE_TESTER,
                camel_case_parser=settings.CAMEL_CASE_PARSER,
            )
        except SwaggerDocumentationError as e:
            long_message = format_response_tester_error(e)
            self.middleware_settings.LOGGER(
                'Incorrect response template returned for %s request to %s. Swagger error: %s',
                request.method,
                request.path,
                str(long_message),
            )
        except CaseError as e:
            self.middleware_settings.LOGGER(f'Found incorrectly cased cased key, `%s` in %s', e.key, e.origin)

    def validate_request_body(self, request: HttpRequest, strict: bool = False) -> Optional[HttpResponse]:
        """
        Validates an incoming request body against the OpenAPI schema request body documentation.

        In case of inconsistencies, a log is logged at a setting-specified log level.

        :param request: HTTP request.
        :param strict: Whether the middleware should reject incoming requests if request body validation fails.
        """
        logger.info('Validating request body for %s request to %s', request.method, request.path)

        # Get the section of the schema relevant for this request
        try:
            request_body_schema = settings.LOADER_CLASS.get_request_body_schema_section(request.path, request.method)
        except (UndocumentedSchemaSectionError, OpenAPISchemaError) as e:
            self.middleware_settings.LOGGER(
                'Failed accessing schema section for %s request to `%s`. Error: %s', request.method, request.path, e
            )
            return None

        # Parse request body
        try:
            value = json.loads(request.body)
        except JSONDecodeError:
            if strict:
                return HttpResponse(content=b'Request body contains invalid JSON', status=400)
            else:
                self.middleware_settings.LOGGER('Failed loading incoming request body as JSON for %s request to %s')
                return None

        # Validate request body against schema
        try:
            SchemaTester(schema=request_body_schema, data=value, case_tester=settings.CASE_TESTER)
        except (SwaggerDocumentationError, CaseError) as e:
            self.middleware_settings.LOGGER(
                'Received bad request body for %s request to %s. Swagger error: \n\n%s',
                request.method,
                request.path,
                str(e),
            )
            if strict:
                example = settings.LOADER_CLASS.get_request_body_example(request.path, request.method)
                msg = f'Request body is invalid. The request body should have the following format: {example}'
                return HttpResponse(content=bytes(msg, 'utf-8'), status=400)

        logger.debug('Response for %s request to %s is correctly documented', request.method, request.path)

    def path_in_endpoints(self, path: str, method: str) -> bool:
        """
        Indicates whether the path belongs in an OpenAPI schema.

        We're only interested in validating requests meant for documented API endpoints.

        :param path: The request path
        :param method: The request method
        :return: Bool indicating whether the request should be handled
        """
        try:
            deparameterized_path, resolved_path = resolve_path(path)
        except ValueError:
            logger.debug('Validation skipped - %s request to %s failed to resolve', method, path)
            return False
        except Resolver404:
            logger.debug('Validation skipped - %s request to %s failed to resolve', method, path)
            return False
        for route in self.endpoints:
            if deparameterized_path == route:
                # Verify that the view has contains the method
                if not hasattr(resolved_path.func.view_class, method.lower()):
                    logger.debug('Validation skipped - %s request method does not exist in the view', method)
                    return False
                logger.debug('%s request to %s is an API request', method, path)
                return True
        logger.debug('Validation skipped - %s request to %s was not found in API endpoints', method, path)
        return False
