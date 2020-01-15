# flake8: noqa  # TODO: Remove
from functools import wraps
from unittest import TestCase

from drf_yasg.openapi import Schema
from requests import Response


def openapi_tester(method, path=None):
    def middle(func):
        def swagger_tester(response: Response, response_schema: Schema, enforce_camel_case: bool = True) -> None:
            """
            Validates input, #todo fetches openapi spec, and calls the test-class.

            :param response: Response object
            :param swagger_schema: OpenAPI Schema
            :param enforce_camel_case: Bool, default True
            :return: None
            :raises: ValidationError #TODO: verify
            """
            if not isinstance(response_schema, Schema):
                raise ValueError(f'`swagger_schema` should be an OpenAPI Schema, not a {type(swagger_schema)}.')

            if not isinstance(enforce_camel_case, bool):
                raise ValueError(f'`check_camel_case` should be a boolean, not a {type(enforce_camel_case)}.')

            from drf_yasg.generators import get_schema

            schema = get_schema()
            # test = OpenAPITester()
            # test.swagger_documentation(response=response, swagger_schema=swagger_schema, enforce_camel_case=enforce_camel_case)

        def validate_inputs():
            """
            Validates decorator inputs.
            """
            if not isinstance(method, str):
                raise TypeError('The input variable `method` should be a string.')
            elif method.lower() != 'dynamic' and type.lower() != 'static':
                raise ValueError('The input variable `method` needs to be "dynamic" or "static".')
            elif method.lower() == 'static':
                if not isinstance(path, str):
                    raise ValueError('Please specify a path to your OpenAPI spec yaml file.')

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            validate_inputs()
            self.assertCorrectSchema = swagger_tester
            func(self, *args, **kwargs)

        return wrapper

    return middle


#
#
# class TestSomething():
#
#     def __init__(self):
#         # setUp equivalent in this example
#         self.schema_path = 'my_schema.yaml'
#
#     @openapi_tester(type='SCHEMA', path='./misc/myschema.yaml')
#     def test_function(self):
#         response = {'success': 'It works!'}
#         self.assertMatchingSchema(name='companies', method='GET', response=response)
#
#     def this_should_fail(self):
#         try:
#             response = {'error': 'This should fail!'}
#             self.assertMatchingSchema(name='companies', method='GET', response=response)
#         except AttributeError:
#             print('The self method is unavailable without the wrapper.')
