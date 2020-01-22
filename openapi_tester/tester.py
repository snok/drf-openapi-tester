from .exceptions import SpecificationError
from .utils import parse_endpoint
from .utils import snake_case, camel_case


class OpenAPITester:
    """
    This class verifies that your OpenAPI schema definition matches the response of your API endpoint.
    It inspects a schema recursively, and verifies that the schema matches the structure of the response at each level.
    """

    def __init__(self, path: str, case: str) -> None:
        self.path = path
        self.case_func = {'camel case': self._is_camel_case, 'snake case': self._is_snake_case, None: self._skip}[case]

    def validate_schema(self, response: dict or list, method: str, endpoint_url: str) -> None:
        """
        Verifies that a swagger schema matches an API response.

        :param response: dict, unpacked response object (response.json())
        :param method: HTTP method
        :param endpoint_url: Path of the endpoint being tested
        :return: None
        """
        if not isinstance(response, dict) and not isinstance(response, list):
            raise ValueError(f'Response object is {type(response)}, ' f'not list or dict. Don\'t forget to pass response.json()')

        # Fetch schema
        from .client import SpecificationFetcher

        s = SpecificationFetcher()

        complete_schema = s.fetch_specification(self.path, 'http://' in self.path or 'https://' in self.path)

        # Fetch sub-schema
        schema = parse_endpoint(complete_schema, method, endpoint_url)

        # Test schema
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
                missing_keys = ', '.join([f'{key}' for key in list(set(schema_keys) - set(response_keys))])
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
            self.case_func(schema_key)
            self.case_func(response_key)

            # If the current object has nested items, want to check these recursively
            nested_schema = schema[schema_key]
            nested_response = response[schema_key]

            if 'items' in nested_schema:
                for key, _ in nested_schema.items():
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
        # For lists, we handle each item individually
        for key, value in schema.items():
            # We're only interested in the sub-items of an array list, not the name or description.
            if key == 'items':

                # drf_yasg makes it very hard to put multiple objects in a list, in documentation
                # so it's mostly safe to just look at the first item (in ref. to response[0])
                # TODO: make sure this actually *does* apply to openapi specs

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
