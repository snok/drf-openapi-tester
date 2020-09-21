import logging
from re import compile
from typing import Callable, Union

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.urls import Resolver404
from django.utils.decorators import sync_only_middleware

from django_swagger_tester.configuration import settings
from django_swagger_tester.utils import Route, copy_response, get_endpoint_paths, resolve_path, safe_validate_response

logger = logging.getLogger('django_swagger_tester')


@sync_only_middleware
class ResponseValidationMiddleware:
    """
    Middleware validates incoming request bodies and outgoing responses with respect to the app's OpenAPI schema.
    """

    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        self.endpoints = get_endpoint_paths()
        self.middleware_settings = settings.middleware_settings.response_validation
        self.exempt_urls = [compile(url_pattern) for url_pattern in self.middleware_settings.validation_exempt_urls]

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

        # skip validation if debug is False
        if not self.middleware_settings.debug:
            return self.get_response(request)
        # ..or if this particular route is ignored in the settings
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
            logger.debug('Validating middleware response')
            copied_response = copy_response(response)
            safe_validate_response(
                response=copied_response,
                path=request.path,
                method=request.method,
                func_logger=self.middleware_settings.logger,
            )
        else:
            logger.debug('Validation skipped - response for %s request to %s has non-JSON content-type', method, path)

        return response

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
                if method.lower() in route_object.resolved_path.func.view_class.__dict__:
                    logger.debug('%s request to %s is an API request', method, path)
                    return True
                else:
                    logger.debug('%s request method does not exist in the view class', method)

        logger.debug('Validation skipped - %s request to %s was not found in API endpoints', method, path)
        return False
