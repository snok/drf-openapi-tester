from unittest import TestCase
from drf_yasg.openapi import Schema
from requests import Response


class OpenAPITester(TestCase):
    """
    This class verifies that your OpenAPI schema definition matches the response of your API endpoint.
    It inspects a schema recursively, and verifies that the schema matches the structure of the response at each level.
    """

    def setUp(self) -> None:
        """
        Runs before every test.
        """
        super(OpenAPITester, self).setUp()
        self.check_camel_case = True

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

    def swagger_documentation(self, response: Response, swagger_schema: Schema, enforce_camel_case: bool = True) -> None:
        """
        Verifies that a swagger schema matches an API response.

        :param response: Response object.
        :param swagger_schema: OpenAPI Schema.
        :param enforce_camel_case: Bool, default True.
        :return: None
        """
        if not isinstance(enforce_camel_case, bool):
            raise ValueError('`check_camel_case` should be a boolean.')

        self.check_camel_case = enforce_camel_case

        if hasattr(swagger_schema, 'properties'):
            self._dict(response.json(), swagger_schema)

        elif hasattr(swagger_schema, 'items'):
            self._list(response.json(), swagger_schema)

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
