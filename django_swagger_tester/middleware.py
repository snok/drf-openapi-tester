import logging
from typing import Callable, Dict, Tuple, Union

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from rest_framework.schemas.generators import EndpointEnumerator

from django_swagger_tester.testing import validate_request_body_schema, validate_response_schema

logger = logging.getLogger('django_swagger_tester')


def get_views() -> Dict[str, Tuple[bool, bool]]:
    """
    Returns a dict with API view routes as the key.

    Values are tuples of bools indicating whether to perform input validation and repsponse validation for that route.
    """
    endpoints = EndpointEnumerator().get_api_endpoints()
    endpoint = endpoints[0]
    return {}


def serializer_from_schema():
    pass


class SwaggerValidationMiddleware(object):
    """
    Enforces input validation on incoming requests and response validation on outgoing responses.

    Inputs are validated to make sure that types correspond with an APIs documented request body, when applicable.

    Responses are validated to make sure they correspond with the example responses documented in the OpenAPI schema.

    Validation is only performed on API views that are decorated with @validate_schema().

    # TODO: Correct description once design is finished
    """

    def __init__(self, get_response: Callable) -> None:
        """
        One-time configuration and initialization.
        """
        self.get_response = get_response
        self.views = get_views()

        # This logic cannot be moved to config.py because apps are not yet initialized when that is executed
        if not apps.is_installed('django_swagger_tester'):
            raise ImproperlyConfigured('django_swagger_tester must be listed in your installed apps')

    def __call__(self, request: HttpRequest) -> Union[HttpRequest, HttpResponse]:
        """
        # TODO: Write docstring

        :param request: HttpRequest from Django
        :return: Passes on the request or response to the next middleware
        """
        path = request.path
        method = request.method.lower()

        print('lalala')

        val_input, val_response = False, False
        if path in self.views:
            val_input, val_response = self.views[path]

        if val_input:
            validate_request_body_schema(serializer=serializer_from_schema(), method=method, route=path)

        # ^ Code above this line is executed before the view and later middleware
        response = self.get_response(request)

        if val_response:
            # Do something else
            val_response(response=response, method=method, route=path)

        return response
