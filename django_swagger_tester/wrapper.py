# import logging
# from functools import wraps
# from typing import Any, Callable
#
# from django.core.exceptions import ImproperlyConfigured
# from rest_framework.request import Request
#
# from django_swagger_tester.configuration import settings
# from django_swagger_tester.exceptions import SwaggerDocumentationError, CaseError
# from django_swagger_tester.testing import validate_response
#
# logger = logging.getLogger('django_swagger_tester')
#
#
# def validate(request_body: bool = False, response: bool = False) -> Any:
#     """
#     Wrapper function to enable middleware-style validation, but for individual API views.
#
#     :param request_body: Whether to validate the request body
#     :param response: Whether to validate the response
#     """
#
#     def outer(fn: Callable) -> Any:
#         @wraps(fn)
#         def inner(*args, **kwargs) -> Any:
#             if not isinstance(args[0], Request):
#                 raise ImproperlyConfigured('The first argument to a view needs to be a Request')
#
#             if request_body:
#                 # input validation function here
#                 print('Request body', args[0].data)
#
#             # ^ Code above this line happens before the view is run
#             output = fn(*args, **kwargs)
#
#             method = args[0].method.upper()
#             path = args[0].path
#
#             if response:
#                 # response validation function here
#                 try:
#                     validate_response(response=output, method=method, route=path)
#                 except SwaggerDocumentationError as e:
#                     settings.MIDDLEWARE.LOGGER(
#                         'Incorrect response template returned for %s request to %s. Swagger error: %s',
#                         method,
#                         path,
#                         str(e),
#                     )
#                 except CaseError as e:
#                     settings.MIDDLEWARE.LOGGER(f'Found incorrectly cased cased key, `%s` in %s', e.key, e.origin)
#             return output
#
#         return inner
#
#     return outer
