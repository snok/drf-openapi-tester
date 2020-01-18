# flake8: noqa TODO: Remove
import json

import yaml
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from drf_yasg.openapi import Schema
from requests import Response
from requests.exceptions import ConnectionError
from rest_framework.test import APITestCase, APIClient
from django.urls import resolve
from django.urls.exceptions import Resolver404
from openapi_tester import oat_settings


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

            self.schema = response.json()

        else:
            try:
                with open(oat_settings['PATH'], 'r') as f:
                    content = f.read()
            except Exception as e:
                raise ImproperlyConfigured(
                    '\n\nCould not read the openapi specification. Please make sure the path setting is correct.' f'\n\nError: {e}'
                )
            if '.json' in oat_settings['PATH'].lower():
                self.schema = json.loads(content)
            elif '.yaml' in oat_settings['PATH'].lower():
                self.schema = yaml.load(content, Loader=yaml.FullLoader)
            else:
                raise ImproperlyConfigured('The specified file path does not seem to point to a JSON or YAML file.')


class OpenAPITester(SwaggerBase):
    """
    This class verifies that your OpenAPI schema definition matches the response of your API endpoint.
    It inspects a schema recursively, and verifies that the schema matches the structure of the response at each level.
    """

    def setUp(self) -> None:
        """
        TODO
        """
        super(OpenAPITester, self).setUp()
        self.case_function = {'CAMELCASE': self._is_camel_case, 'SNAKECASE': self._is_snake_case, None: self._skip}[oat_settings['CASE']]

    def swagger_documentation(self, response: Response, method: str, path: str) -> None:
        """
        Verifies that a swagger schema matches an API response.

        :param response: Response object
        :param method: HTTP method
        :param path: Path of the endpoint being tested
        :return: None
        :raises: TODO
        """
        # Replicate the dict/list logic using the schema. Specify a method and a path (use resolve) in test.py and
        #
        try:
            resolved_path = resolve(path)
        except Resolver404:
            raise ValueError(f'Could not resolve path `{path}`')

    #
    # if hasattr(swagger_schema, 'properties'):
    #     self._dict(response.json(), swagger_schema)
    #
    # elif hasattr(swagger_schema, 'items'):
    #     self._list(response.json(), swagger_schema)

    def get_endpoint(schema: dict, path: str, method: str) -> dict:
        """
        Returns the part of the schema we want to test for any single test.

        :param spec: OpenAPI specification
        :return: dict
        """
        methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']
        if method.casefold() not in methods:
            raise ValueError(f'Invalid value for `method`. Needs to be one of: {", ".join([i.upper() for i in methods])}.')
        return spec['paths'][path.casefold()][method.casefold()]

    def _dict(self, response_dict: dict, swagger_schema: Schema) -> None:
        """
        Verifies that a schema dict matches a response dict.

        :param response_dict: dict
        :param swagger_schema: Schema
        :return: None
        """
        # Data should be a dict
        self.assertEqual(type(response_dict), dict)

        swagger_schema_keys = swagger_schema.properties.keys()
        response_dict_keys = response_dict.keys()

        # The number of keys in each dictionary should match
        if len(swagger_schema_keys) != len(response_dict_keys):
            # There are more keys returned than documented
            if len(set(response_dict_keys) - set(swagger_schema_keys)):
                missing_keys = ', '.join(list(set(response_dict_keys) - set(swagger_schema_keys)))
                raise ValueError(f'The following keys are missing from the swagger schema: {missing_keys}')
            # There are fewer keys returned than documented
            else:
                missing_keys = ', '.join(list(set(swagger_schema_keys) - set(response_dict_keys)))
                raise ValueError(f'The following keys are missing from the response body schema: {missing_keys}')

        # And the keys of the swagger schema should be found in the response and vice versa
        for swagger_key, response_data_key in zip(response_dict_keys, swagger_schema_keys):
            self.assertIn(swagger_key, response_data_key)  # Schema keys should be in the response
            self.assertIn(response_data_key, swagger_schema_keys)  # and the response keys should also all be in the schema

            # Dict keys should be camelCased
            if self.check_camel_case:
                self.assertTrue(self._is_camel_case(swagger_key), msg=f'Swagger key, `{swagger_key}`, should be camel-cased.')
                self.assertTrue(self._is_camel_case(response_data_key), msg=f'Response key, `{response_data_key}`, should be camel-cased.')

            # If the item has nested items, we also want to check these
            nested_schema = swagger_schema.properties[swagger_key]
            nested_response_dict = response_dict[swagger_key]

            if hasattr(nested_schema, 'items'):
                for item in nested_schema.items():
                    # A schema definition includes overhead that we're not interested in comparing to the response.
                    # Here, we're only iterested in the sub-items of the list, not the name or description.
                    if 'items' in item:
                        self._list(nested_response_dict, item[1])  # Item is a tuple: (key, value)

            elif hasattr(nested_schema, 'properties'):
                self._dict(response_dict[swagger_key], nested_schema)

    def _list(self, response_list: list, swagger_schema: Schema) -> None:
        """
        Verifies that the response item matches the swagger schema documentation, when the schema layer is an ordered dict.
        :param response_list: dict.
        :param swagger_schema: Schema.
        :return: None.
        """
        # Data should be a list
        self.assertEqual(type(response_list), list)

        # And we handle each element in the list individually
        for item in swagger_schema.items():

            # We're only interested in the sub-items of the list, not the name or description.
            if 'items' in item:
                nested_schema = item[1]  # Item is a tuple: (key, value)
                if hasattr(nested_schema, 'properties'):
                    self._dict(response_list[0], nested_schema)

                elif hasattr(nested_schema, 'items'):
                    self._list(response_list[0], nested_schema)

    @staticmethod
    def _is_camel_case(key: str) -> bool:
        # TODO: Replace with regex
        # This is just a placeholder
        first_letter = True
        for letter in key:
            uppercase = letter == letter.upper()

            # First letter should be lower-case
            if first_letter and uppercase:
                return False
            if first_letter and not uppercase:
                first_letter = False

            # No underscores
            if letter == '_':
                return False
        return True

    @staticmethod
    def _is_snake_case(key: str) -> bool:
        # TODO: Replace with regex
        # This is just a placeholder
        first_letter = True
        for letter in key:
            uppercase = letter == letter.upper()

            # First letter should be lower-case
            if first_letter and uppercase:
                return False
            if first_letter and not uppercase:
                first_letter = False

            # No underscores
            if letter == '_':
                return False
        return True

    @staticmethod
    def _skip() -> bool:
        return False
