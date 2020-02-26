import logging
from typing import Callable, Union

from requests import Response

from openapi_tester.case_checks import case_check
from openapi_tester.configuration import load_settings
from openapi_tester.dynamic.get_schema import fetch_generated_schema
from openapi_tester.exceptions import SpecificationError
from openapi_tester.static.get_schema import fetch_from_dir
from openapi_tester.static.parse import parse_endpoint

logger = logging.getLogger('openapi_tester')


def validate_schema(response: Response, method: str, endpoint_url: str) -> None:
    """
    This function verifies that your OpenAPI schema definition matches the response of your API endpoint.
    It inspects your schema recursively, and verifies that the schema matches the structure of the response,
    at each level.

    :param response: dict, unpacked response object (response.json())
    :param method: HTTP method ('get', 'put', 'post', ...)
    :param endpoint_url: Relative path of the endpoint being tested
    :return: None
    """
    # Load settings
    schema, case, path = load_settings()
    case_func = case_check(case)

    try:
        data = response.json()
    except Exception as e:
        raise ValueError(f'Unable to unpack response object. Hint: make sure you are passing response, not response.json(). ' f'Error: {e}')

    # Fetch schema
    if schema == 'static':
        complete_schema = fetch_from_dir(path=path)
        # Get the part of the schema relating to the endpoints success-response
        schema = parse_endpoint(schema=complete_schema, method=method, endpoint_url=endpoint_url)
    else:
        schema = fetch_generated_schema(url=endpoint_url, method=method)

    # Test schema
    if 'properties' in schema:
        _dict(schema=schema, data=data, case_func=case_func)

    elif 'items' in schema:
        _list(schema=schema, data=data, case_func=case_func)

    else:
        raise ValueError('Schema is missing properties and items keys. Schema is not testable.')


def _dict(schema: dict, data: Union[list, dict], case_func: Callable) -> None:
    """
    Verifies that a schema dict matches a response dict.

    :param schema: dict
    :param data: list or dict
    :param case_func: function
    :return: None
    """
    logger.debug('Verifying that response dict layer matches schema layer')

    if not isinstance(data, dict):
        raise SpecificationError(f"The response is {type(data)} where it should be <class 'dict'>")

    schema_keys = schema.keys()
    response_keys = data.keys()

    # Check that the number of keys in each dictionary matches
    if len(schema_keys) != len(response_keys):
        logger.debug('The number of schema dict elements do not match the number of response dict elements')
        # If there are more keys returned than documented
        if len(set(response_keys) - set(schema_keys)):
            missing_keys = ', '.join([f'`{key}`' for key in list(set(response_keys) - set(schema_keys))])
            raise SpecificationError(f'The following properties seem to be missing from your OpenAPI/Swagger documentation: {missing_keys}')
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
        nested_data = data[schema_key]

        if 'items' in nested_schema:
            for key, _ in nested_schema.items():
                # A schema definition includes overhead that we're not interested in comparing to the response.
                # Here, we're only interested in the sub-items of the list, not the name or description.
                if key == 'items':
                    _list(schema=nested_schema, data=nested_data, case_func=case_func)  # Item is a tuple: (key, value)

        elif 'properties' in nested_schema:
            _dict(schema=nested_schema, data=nested_data, case_func=case_func)


def _list(schema: dict, data: Union[list, dict], case_func: Callable) -> None:
    """
    Verifies that the response item matches the schema documentation, when the schema layer is an array.

    :param schema: dict
    :param data: dict.
    :param case_func: function
    :return: None.
    """
    logger.debug('Verifying that response list layer matches schema layer')

    if not isinstance(data, list):
        raise SpecificationError(f"The response is {type(data)} when it should be <class 'list'>")

    if not data:
        raise SpecificationError('Schema contains a list element that is not found in the response')

    # For lists, we handle each item individually
    # We're only interested in the sub-items of an array list, not the name or description.
    item = schema['items']

    if 'properties' in item and item['properties']:
        [_dict(schema=item['properties'], data=data[i], case_func=case_func) for i in range(len(data))]

    elif 'items' in item and item['items']:
        [_list(schema=item, data=data[i], case_func=case_func) for i in range(len(data))]

    elif len(data) > 1 and data[0]:
        raise SpecificationError('Response contains a list element that is not found in the schema')
