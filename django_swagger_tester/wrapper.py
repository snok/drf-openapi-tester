import logging
from functools import wraps
from typing import Any, Callable

from django.core.exceptions import ImproperlyConfigured
from rest_framework.request import Request

from django_swagger_tester.configuration import settings
from django_swagger_tester.middleware import copy_and_parse_response, validate_middleware_response

logger = logging.getLogger('django_swagger_tester')


def validate_response() -> Any:
    """
    Wrapper function to enable middleware-style validation, but for individual API views.
    """

    def outer(fn: Callable) -> Any:
        @wraps(fn)
        def inner(*args, **kwargs) -> Any:

            if not isinstance(args[0], Request):
                raise ImproperlyConfigured('The first argument to a view needs to be a Request')
            else:
                request = args[0]

            response = fn(*args, **kwargs)

            # code below this line is identical to the code we run in the middleware -

            logger.debug('Validating response')
            copied_response = copy_and_parse_response(response)
            validate_middleware_response(
                response=copied_response,
                path=request.path,
                method=request.method,
                func_logger=settings.WRAPPERS.RESPONSE_VALIDATION.LOGGER,
            )

            return response

        return inner

    return outer
