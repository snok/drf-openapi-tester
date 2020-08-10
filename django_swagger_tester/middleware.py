import json
import logging
from json import JSONDecodeError
from typing import Callable, Union, Optional
from re import compile
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from rest_framework.response import Response

from django_swagger_tester.configuration import settings
from django_swagger_tester.schema_validation.case import ResponseCaseTester, SchemaCaseTester
from django_swagger_tester.schema_validation.schema_tester import SchemaTester
from django_swagger_tester.schema_validation.utils import resolve_path, get_endpoint_paths

logger = logging.getLogger('django_swagger_tester')

"""
Note:

The middleware should have two modes:

- Default
- Strict

Default should log errors when one of the three validation types (response, uri param, request body) fail.
Strict should reject incoming requests when uri param og request body validation fails.
"""


class SwaggerValidationMiddleware(object):
    """
    # TODO: Verify or update before release

    This middleware performs three levels of validation:

    - Request body validation, with respect to the documented request body from the OpenAPI schema
    - URI parameter validation, with respect to the documented URI parameters in the OpenAPI schema
    - Response validation, with respect to the documented responses in the OpenAPI schema

    With the default settings, a failure in one of these levels of validation will log a message
    at the specified log level (the default is to log as an error),

    If strict validation is specified in the package settings, failures in request validation will
    return a 400-response, indicating what went wrong.
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
        Method is called for every incoming request and outgoing response.

        Validates

            - incoming request bodies,
            - incoming URI params, and
            - outgoing responses

        with respect to the application's OpenAPI schema.

        :param request: HttpRequest from Django
        :return: Passes on the request or response to the next middleware
        """
        if request.headers['Content-Type'] not in ['application/json']:
            # Non-JSON content types are not handled
            handle_request = False
        elif any(m.match(request.path_info.lstrip('/')) for m in self.exempt_urls):
            # Skip handling for ignored routes
            handle_request = False
        else:
            # Handle request if path is a valid endpoint
            handle_request = self.path_in_endpoints(request.path, request.method)

        validate_request_body = handle_request and request.body and self.middleware_settings.VALIDATE_REQUEST_BODY
        validate_response = self.middleware_settings.VALIDATE_RESPONSE

        if validate_request_body:

            potential_response = self.validate_request_body(request)
            if potential_response is not None:
                return potential_response

        # ^ Code above this line is executed before the view and later middleware
        response = self.get_response(request)

        if validate_response:
            self.validate_response(response, request)

        return response

    def validate_response(self, response: Response, request: HttpRequest) -> None:
        """
        Validates an outgoing response object against the OpenAPI schema response documentation.

        In case of inconsistencies, a log is logged, notifying system administrators.

        :param response: HTTP response
        :param request: HTTP request
        """
        logger.info('Validating response for %s request to %s', request.method, request.path)
        response_schema = settings.LOADER_CLASS.get_response_schema_section(
            route=request.path, status_code=response.status_code, method=request.method
        )
        tester = SchemaTester(response_schema=response_schema, response_data=response.data)
        if tester.error:
            self.middleware_settings.LOGGER(
                'Incorrect response template returned for %s request to %s. Swagger error: %s',
                request.method,
                request.path,
                tester.error,
            )
        ResponseCaseTester(response_data=response.data)
        SchemaCaseTester(schema=response_schema)

    def validate_request_body(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Validates an incoming request body against the OpenAPI schema request body documentation.

        In case of inconsistencies, a log is logged, notifying system administrators.

        If the middleware settings `STRICT` is set to True, the middleware will also actively reject a bad
        incoming request completely, returning a 400 with the appropriate error message.

        :param request: HTTP request
        """
        logger.info('Validating request body for %s request to %s', request.method, request.path)

        # Fetch the OpenAPI schema section related to the request body of this endpoint
        request_body_schema = settings.LOADER_CLASS.get_request_body_schema_section(request.path, request.method)

        try:
            # Parse request body as the correct type
            value = json.loads(request.body)
        except JSONDecodeError:
            # Handle parsing failure
            if self.middleware_settings.STRICT:
                # Return 400 if strict
                return HttpResponse(content=b'Request body contains invalid JSON', status=400)
            else:
                # Log otherwise
                self.middleware_settings.LOGGER('Failed loading incoming request body as JSON for %s request to %s')
        else:
            # Run schema tester on the request body and the request body schema section
            tester = SchemaTester(request_body_schema, value)
            if tester.error:
                # Handle bad request body error
                if self.middleware_settings.STRICT:
                    # Return 400 if strict
                    example = settings.LOADER_CLASS.get_request_body_example(request.path, request.method)
                    msg = f'Request body is invalid. The request body should have the following format: {example}'
                    return HttpResponse(content=bytes(msg, 'utf-8'), status=400)

                # Log whether it's strict or not
                self.middleware_settings.LOGGER(
                    'Received bad request body for %s request to %s. Swagger error: \n\n%s',
                    request.method,
                    request.path,
                    tester.error,
                )
        return None

    def path_in_endpoints(self, path: str, method: str) -> bool:
        """
        Indicates whether the path belongs in an OpenAPI schema.

        We're only interested in validating requests meant for documented API endpoints.

        :param path: The request path
        :param method: The request method
        :return: Bool indicating whether the request should be handled
        """
        try:
            resolved_path = resolve_path(path)
        except ValueError:
            logger.debug('Failed to resolve path for %s request to %s. Skipping validation', method, path)
            return False
        else:
            for route in self.endpoints:
                if resolved_path == route:
                    logger.debug('Request to %s is an API request', path)
                    return True
        return False
