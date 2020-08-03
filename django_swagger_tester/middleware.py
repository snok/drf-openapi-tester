import logging
from typing import Callable, Union

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from rest_framework.schemas.generators import EndpointEnumerator

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.testing import validate_response_schema
from django_swagger_tester.utils import resolve_path

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
    at the specied log level (the default is to log as an error),

    If strict validation is specified in the package settings, failures in request validation will
    return a 400-response, indicating what went wrong.
    """

    def __init__(self, get_response: Callable) -> None:
        """
        One-time configuration and initialization of the middleware.
        """
        self.endpoints = EndpointEnumerator().get_api_endpoints()  # TODO: Replace with a local copy
        self.get_response = get_response

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
        path = request.path
        method = request.method.upper()

        api_request = False
        resolved_path = resolve_path(path)

        # Determine whether the request is being made to an API
        for route, _, _ in self.endpoints:
            if resolved_path == route:
                logger.debug('Request to %s is an API request', path)
                api_request = True
                break

        if api_request and request.body:
            print('--> Validate request body')
            # TODO: Write function

        # ^ Code above this line is executed before the view and later middleware
        response = self.get_response(request)

        if api_request:
            copied_response = response
            copied_response.json = lambda: response.data
            try:
                validate_response_schema(response=copied_response, method=method, route=path)
            except SwaggerDocumentationError as e:
                logger.error(
                    'Incorrect response template returned for %s request to %s. ' 'Swagger error: \n\n%s',
                    method,
                    path,
                    e,
                )
            except Exception as e:
                # TODO: Change
                logger.critical('DONT UNDERSTAND THIS: %s', e)
                raise

        return response
