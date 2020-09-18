import logging
from typing import Any, Callable

from django.core.exceptions import ImproperlyConfigured
from rest_framework.request import Request

from django_swagger_tester.configuration import settings
from django_swagger_tester.middleware import validate_middleware_response
from django_swagger_tester.utils import copy_wrapper_response

logger = logging.getLogger('django_swagger_tester')


def validate_response(fn: Callable) -> Any:
    """
    Wrapper function to enable middleware-style validation, but for individual API views.
    """

    def outer(*args, **kwargs) -> Any:

        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        else:
            raise ImproperlyConfigured('The validate_response wrapper function needs to wrap a DRF APIView method')

        response = fn(*args, **kwargs)

        # code below this line is identical to the code we run in the middleware -

        logger.debug('Validating wrapper response')
        copied_response = copy_wrapper_response(response)
        validate_middleware_response(
            response=copied_response,
            path=request.path,
            method=request.method,
            func_logger=settings.WRAPPERS.RESPONSE_VALIDATION.LOGGER,
        )

        return response

    return outer
