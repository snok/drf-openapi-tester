# flake8: noqa TODO: Remove
import json

import yaml
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.urls import resolve
from django.urls.exceptions import Resolver404
from drf_yasg.openapi import Schema
from requests import Response
from requests.exceptions import ConnectionError
from rest_framework.test import APITestCase, APIClient

from openapi_tester import oat_settings
from .exceptions import SpecificationError
from .utils import snake_case, camel_case


class SwaggerBase(APITestCase):
    client = APIClient()

    def _authenticate(self) -> None:
        """
        Get valid user and attach credentials to client
        """
        user, _ = User.objects.update_or_create(username='testuser')
        self.client.force_authenticate(user=user)

    def fetch_specification(self) -> None:
        """
        Fetches the hosted OpenAPI specification using the DRF APIClient.
        """
        if 'http://' in oat_settings['PATH'] or 'https://' in oat_settings['PATH']:
            try:
                self._authenticate()
                response = self.client.get(oat_settings['PATH'], format='json')
            except ConnectionError as e:
                raise ConnectionError(
                    '\n\nNot able to connect to the specified openapi url. '
                    f'Please make sure the specified path is correct.\n\nError: {e}'
                )
            if 400 <= response.status_code <= 600:
                raise ImproperlyConfigured(
                    '\n\nCould not fetch the openapi specification. Please make sure your documentation is '
                    f'set to public.\n\nAPI response code: {response.status_code}\nAPI response: {response.text}'
                )

            self.complete_schema = response.json()

        else:
            try:
                with open(oat_settings['PATH'], 'r') as f:
                    content = f.read()
            except Exception as e:
                raise ImproperlyConfigured(
                    '\n\nCould not read the openapi specification. Please make sure the path setting is correct.' f'\n\nError: {e}'
                )
            if '.json' in oat_settings['PATH'].lower():
                self.complete_schema = json.loads(content)
            elif '.yaml' in oat_settings['PATH'].lower():
                self.complete_schema = yaml.load(content, Loader=yaml.FullLoader)
            else:
                raise ImproperlyConfigured('The specified file path does not seem to point to a JSON or YAML file.')


class OpenAPITester(SwaggerBase):
    """
    This class verifies that your OpenAPI schema definition matches the response of your API endpoint.
    It inspects a schema recursively, and verifies that the schema matches the structure of the response at each level.
    """

    @staticmethod
    def _get_endpoint_200_response(schema: dict, method: str, path: str) -> dict:
        """
        Returns the part of the schema we want to test for any single test.

        :param spec: OpenAPI specification
        :return: dict
        """
        methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']
        if method.casefold() not in methods:
            raise ValueError(f'Invalid value for `method`. Needs to be one of: {", ".join([i.upper() for i in methods])}.')
        try:
            resolved_path = resolve(path)
        except Resolver404:
            raise ValueError(f'Could not resolve path `{path}`')

        endpoints = [key for key in schema['paths']]
        matched_endpoints = [endpoint for endpoint in endpoints if endpoint in resolved_path.route]

        if len(matched_endpoints) == 0:
            raise ValueError('Could not match the resolved url to a documented endpoint in the OpenAPI specification')
        elif len(matched_endpoints) == 1:
            matched_endpoint = matched_endpoints[0]
        else:
            # We probably shouldn't ever let this happen
            # TODO: Try to make it happen in testing, and work out a better way to do this
            raise ValueError('Matched the resolved urls to too many endpoints.')

        return schema['paths'][matched_endpoint][method.casefold()]['responses']['200']['schema']

    def swagger_documentation(self, response: json, method: str, path: str) -> None:
        """
        Verifies that a swagger schema matches an API response.

        :param response: dict, unpacked response object (response.json())
        :param method: HTTP method
        :param path: Path of the endpoint being tested
        :return: None
        :raises: TODO
        """
        # Replicate the dict/list logic using the schema. Specify a method and a path (use resolve) in test.py and
        #
        self.fetch_specification()
        self.case_function = {'CAMELCASE': self._is_camel_case, 'SNAKECASE': self._is_snake_case, None: self._skip}[oat_settings['CASE']]
        schema = self._get_endpoint_200_response(self.complete_schema, method, path)

        if hasattr(schema, 'properties'):
            self._dict(schema, response)

        elif hasattr(schema, 'items'):
            self._list(schema, response)

    def _dict(self, schema: dict, response: dict) -> None:
        """
        Verifies that a schema dict matches a response dict.

        :param schema: dict
        :param response: dict
        :return: None
        """
        print('\n\n-------- dict -------\n', schema, '\n\n', response, '\n-------- /dict -------')  # TODO: remove

        schema_keys = schema.keys()
        response_keys = response.keys()

        # Check that the number of keys in each dictionary matches
        if len(schema_keys) != len(response_keys):
            # If there are more keys returned than documented
            if len(set(response_keys) - set(schema_keys)):
                missing_keys = ', '.join([f'{key}' for key in list(set(response_keys) - set(schema_keys))])
                raise SpecificationError(
                    f'The following properties seem to be missing from ' f'you OpenAPI/Swagger documentation: {missing_keys}'
                )
            # If there are fewer keys returned than documented
            else:
                missing_keys = ', '.join([f'{key}' for key in list(set(swagger_schema_keys) - set(response_dict_keys))])
                raise SpecificationError(f'The following properties seem to be missing from your response body' f': {missing_keys}')

        # Check that all the key values match
        for schema_key, response_key in zip(schema_keys, response_keys):

            # schema keys should be in the response
            if schema_key not in response_keys:
                raise SpecificationError(f'Schema key `{schema_key}` was not found in the API response')

            # and the response keys should also all be in the schema
            elif response_key not in schema_keys:
                raise SpecificationError(f'Response key `{response_key}` is missing from your API documentation')

            # Run our case function (checks for camelCase or snake_case, or skips check when the CASE param is None)
            self.case_function(schema_key)
            self.case_function(response_key)

            # If the current object has nested items, want to check these recursively
            nested_schema = schema[schema_key]
            nested_response = response[schema_key]

            if 'items' in nested_schema:
                for key, value in nested_schema.items():
                    # A schema definition includes overhead that we're not interested in comparing to the response.
                    # Here, we're only interested in the sub-items of the list, not the name or description.
                    if key == 'items':
                        self._list(nested_schema, nested_response)  # Item is a tuple: (key, value)

            elif 'properties' in nested_schema:
                self._dict(nested_schema, nested_response)

    def _list(self, schema: dict, response: list) -> None:
        """
        Verifies that the response item matches the schema documentation, when the schema layer is an array.

        :param schema: dict
        :param response: dict.
        :return: None.
        """
        print('\n\n-------- list -------\n', schema, '\n\n', response, '\n-------- /list -------')  # TODO: remove

        # For lists, we handle each item individually
        for key, value in schema.items():
            # We're only interested in the sub-items of an array list, not the name or description.
            if key == 'items':

                # drf_yasg makes it very hard to put multiple objects in a list, in documentation
                # so it's mostly safe to just look at the first item (in ref. to response[0])
                # TODO: make sure this applies to openapi specs

                if 'properties' in value:
                    self._dict(value['properties'], response[0])

                elif 'items' in value:
                    self._list(value, response[0])

    @staticmethod
    def _is_camel_case(key: str) -> None:
        """
        Asserts that a value is camelCased.

        :param key: str
        :return: None
        :raises: SpecificationError
        """
        if camel_case(key) != key:
            raise SpecificationError(f'The property `{key}` is not properly camelCased')

    @staticmethod
    def _is_snake_case(key: str) -> None:
        """
        Asserts that a value is snake_cased.

        :param key: str
        :return: None
        :raises: SpecificationError
        """
        if snake_case(key) != key:
            raise SpecificationError(f'The property `{key}` is not properly snake_cased')

    @staticmethod
    def _skip() -> None:
        """
        Skips case assertion.

        :return: None
        """
        pass
