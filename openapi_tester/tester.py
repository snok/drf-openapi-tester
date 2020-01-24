import logging
from typing import Callable
from typing import Union

from .case import case_check
from .client import fetch_specification
from .exceptions import SpecificationError
from .settings import load_settings
from .parse import parse_endpoint

logger = logging.getLogger('openapi-tester')


def validate_schema(response: Union[dict, list], method: str, endpoint_url: str) -> None:
    """
    This function verifies that your OpenAPI schema definition matches the response of your API endpoint.
    It inspects your schema recursively, and verifies that the schema matches the structure of the response,
    at each level.

    :param response: dict, unpacked response object (response.json())
    :param method: HTTP method
    :param endpoint_url: Path of the endpoint being tested
    :return: None
    """
    # Load settings
    path, case = load_settings()
    case_func = case_check(case)

    if not isinstance(response, dict) and not isinstance(response, list):
        raise ValueError(f'Response object is {type(response)}, not a dict. Hint: make sure you are passing response.json()')

    # Fetch schema
    complete_schema = fetch_specification(path=path, is_url='http://' in path or 'https://' in path)

    # Get the part of the schema relating to the endpoints success-response
    schema = parse_endpoint(schema=complete_schema, method=method, endpoint_url=endpoint_url)

    # Test schema
    if hasattr(schema, 'properties'):
        _dict(schema=schema, response=response, case_func=case_func)

    elif hasattr(schema, 'items'):
        _list(schema=schema, response=response, case_func=case_func)

    else:
        raise ValueError('Schema is missing properties and items keys. Schema is not testable.')


def _dict(schema: dict, response: Union[list, dict], case_func: Callable) -> None:
    """
    Verifies that a schema dict matches a response dict.

    :param schema: dict
    :param response: list or dict
    :param case_func: function
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
        case_func(schema_key)
        case_func(response_key)

        # If the current object has nested items, want to check these recursively
        nested_schema = schema[schema_key]
        nested_response = response[schema_key]

        if 'items' in nested_schema:
            for key, _ in nested_schema.items():
                # A schema definition includes overhead that we're not interested in comparing to the response.
                # Here, we're only interested in the sub-items of the list, not the name or description.
                if key == 'items':
                    _list(schema=nested_schema, response=nested_response, case_func=case_func)  # Item is a tuple: (key, value)

        elif 'properties' in nested_schema:
            _dict(schema=nested_schema, response=nested_response, case_func=case_func)


def _list(schema: dict, response: Union[list, dict], case_func: Callable) -> None:
    """
    Verifies that the response item matches the schema documentation, when the schema layer is an array.

    :param schema: dict
    :param response: dict.
    :param case_func: function
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
                _dict(schema=value['properties'], response=response[0], case_func=case_func)

            elif 'items' in value:
                _list(schema=value, response=response[0], case_func=case_func)
