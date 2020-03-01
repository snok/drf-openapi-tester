import logging
from typing import Callable, Union, Any

from pip._vendor.requests import Response

from openapi_tester.case_checks import case_check
from openapi_tester.configuration import load_settings
from openapi_tester.dynamic.get_schema import fetch_generated_schema
from openapi_tester.exceptions import OpenAPISchemaError
from openapi_tester.static.get_schema import fetch_from_dir
from openapi_tester.static.parse import parse_endpoint

logger = logging.getLogger('openapi_tester')


def validate_schema(response: Response, method: str, endpoint_url: str) -> None:
    """
    This function verifies that your OpenAPI schema definition matches the response of your API endpoint.
    It inspects your schema recursively, and verifies that the schema matches the structure of the response, at every level.

    :param response: HTTP response
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
        logger.exception('Unable to open response object')
        raise ValueError(
            f'Unable to unpack response object. ' f'Make sure you are passing response, and not response.json(). Error: {e}')

    # Fetch schema
    if schema == 'static':
        complete_schema = fetch_from_dir(path=path)
        # Get the part of the schema relating to the endpoints success-response
        schema = parse_endpoint(schema=complete_schema, method=method, endpoint_url=endpoint_url)
    else:
        schema = fetch_generated_schema(url=endpoint_url, method=method)

    # Test schema
    if not schema:
        raise OpenAPISchemaError('The OpenAPI schema is undefined. Schema is not testable.')
    if schema['type'] == 'object':
        _dict(schema=schema, data=data, case_func=case_func)
    elif schema['type'] == 'array':
        _list(schema=schema, data=data, case_func=case_func)
    elif schema['type'] == 'string' or schema['type'] == 'boolean' or schema['type'] == 'integer':
        _item(schema=schema, data=data)
    else:
        raise Exception(f'Unexpected error.\nSchema: {schema}\n Response: {data}')  # TODO: Remove after testing


def _dict(schema: dict, data: Union[list, dict], case_func: Callable) -> None:
    """
    Verifies that a schema dict matches a response dict.

    :param schema: OpenAPI schema
    :param data: Response data
    :param case_func: Function that verifies string casing matches the documented preference (e.g., camel case)
    :return: None
    """
    logger.debug('Verifying that response dict layer matches schema layer')

    # Check that the response data is the right type and unpack dict keys
    if not isinstance(data, dict):
        if isinstance(data, list) and len(data) == 0:
            # If a list of objects is documented, but no objects are included in the response, that doesnt make the
            # documentation incorrect.
            return
        else:
            raise OpenAPISchemaError(f"The response is {type(data)} where it should be <class 'dict'>")
    schema_keys = schema['properties'].keys()
    response_keys = data.keys()

    # Verify that the length of both dicts match - A length mismatch will always indicate an error
    if len(schema_keys) != len(response_keys):
        logger.debug('The number of schema dict elements does not match the number of response dict elements')
        if len(set(response_keys)) > len(set(schema_keys)):
            missing_keys = ', '.join([f'`{key}`' for key in list(set(response_keys) - set(schema_keys))])
            raise OpenAPISchemaError(
                f'The following properties seem to be missing from your OpenAPI/Swagger documentation: {missing_keys}')
        else:
            missing_keys = ', '.join([f'{key}' for key in list(set(schema_keys) - set(response_keys))])
            raise OpenAPISchemaError(
                f'The following properties seem to be missing from your response body' f': {missing_keys}')

    for schema_key, response_key in zip(schema_keys, response_keys):

        # Check the keys for case inconsistencies
        case_func(schema_key)
        case_func(response_key)

        # Check that each element in the schema exists in the response, and vice versa
        if schema_key not in response_keys:
            raise OpenAPISchemaError(
                f'Schema key `{schema_key}` was not found in the API response. '
                f'Response keys include: {", ".join([i for i in data.keys()])}'
            )
        elif response_key not in schema_keys:
            raise OpenAPISchemaError(f'Response key `{response_key}` is missing from your API documentation')

        # Check what further check is needed for the values contained in the dict

        schema_value = schema['properties'][schema_key]
        response_value = data[schema_key]

        if schema_value['type'] == 'object':
            logger.debug('Calling _dict from _dict. Response: %s, Schema', response_value, schema_value)
            _dict(schema=schema_value, data=response_value, case_func=case_func)
        elif schema_value['type'] == 'array':
            _list(schema=schema_value, data=response_value, case_func=case_func)
        elif schema_value['type'] == 'string' or schema_value['type'] == 'boolean' or schema_value['type'] == 'integer':
            _item(schema=schema_value, data=response_value)
        else:
            raise Exception(f'Unexpected error.\nSchema: {schema}\n Response: {data}')  # TODO: Remove after testing


def _list(schema: dict, data: Union[list, dict], case_func: Callable) -> None:
    """
    Verifies that the response item matches the schema documentation, when the schema layer is an array.

    :param schema: OpenAPI schema
    :param data: Response data
    :param case_func: Function that verifies string casing matches the documented preference (e.g., camel case)
    :return: None.
    """
    logger.debug('Verifying that response list layer matches schema layer')
    if not isinstance(data, list):
        raise OpenAPISchemaError(f"The response is {type(data)} when it should be <class 'list'>")

    # A schema array can only hold one item, e.g., {"type": "array", "items": {"type": "object", "properties": {...}}}
    # At the same time we want to test each of the response objects, as they *should* match the schema.
    item = schema['items']

    for index in range(len(data)):

        # If the schema says all listed items are to be dictionaries and the dictionaries should have values...
        if item['type'] == 'object' and item['properties']:
            # ... then check those values
            _dict(schema=item, data=data[index], case_func=case_func)

        # If the schema says all listed items are to be dicts, and the response has values but the schema is empty
        elif (item['type'] == 'object' and not item['properties']) and data[index]:
            # ... then raise an error
            raise OpenAPISchemaError(f'Response dict contains value `{data[index]}` '
                                     f'where schema suggests there should be an empty dict.')

        # If the schema says all listed items are to be arrays and the lists should have values
        elif item['type'] == 'array' and item['items']:
            # ... then check those values
            _list(schema=item, data=data[index], case_func=case_func)

        # If the schema says all listed items are to be arrays, and the response has values but the schema is empty
        elif (item['type'] == 'array' and not item['items']) and data[index]:
            raise OpenAPISchemaError(f'Response list contains value `{data[index]}` '
                                     f'where schema suggests there should be an empty list.')

        elif item['type'] == 'string' or item['type'] == 'boolean' or item['type'] == 'integer':
            _item(schema=item, data=data)

        else:
            raise Exception(f'Unexpected error.\nSchema: {schema}\n Response: {data}')  # TODO: Remove after testing


def _item(schema: dict, data: Any) -> None:
    """
    Verifies that a response value matches the example value in the schema.

    :param schema: OpenAPI schema
    :param data:
    :return:
    """
    if schema['type'] == 'boolean':
        if not isinstance(data, bool) and not (
                isinstance(data, str) and (data.lower() == 'true' or data.lower() == 'false')):
            raise OpenAPISchemaError(
                f"The example value `{schema['example']}` does not match the specified data type <type 'bool'>.")

    elif schema['type'] == 'string':
        if not isinstance(data, str):
            raise OpenAPISchemaError(
                f"The example value `{schema['example']}` does not match the specified data type <type 'str>'.")

    elif schema['type'] == 'integer':
        if not isinstance(data, int):
            raise OpenAPISchemaError(
                f"The example value `{schema['example']}` does not match the specified data type <class 'int'>.")

    else:
        raise Exception(f'Unexpected error.\nSchema: {schema}\n Response: {data}')  # TODO: Remove after testing
