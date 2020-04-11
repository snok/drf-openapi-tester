import logging
from collections import KeysView
from typing import Any

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.utils import replace_refs

logger = logging.getLogger('django_swagger_tester')


def get_response_schema(schema: dict, route: str, method: str, status_code: int) -> dict:
    """
    Indexes schema by url, HTTP method, and status code to get the section of a schema related to a specific response.

    :param schema: Full OpenAPI schema
    :param route: Schema-compatible path
    :param method: HTTP request method
    :param status_code: HTTP response code
    :return Response sub-section of the schema
    """
    schema = replace_refs(schema)
    try:
        logger.debug('Indexing schema by route `%s`', route)
        path_indexed_schema = schema['paths'][route]
    except KeyError:
        raise SwaggerDocumentationError(
            f'Failed initialization\n\nError: Unsuccessfully tried to index the OpenAPI schema by '
            f'`{route}`, but the key does not exist in the schema.'
            f'\n\nFor debugging purposes: valid urls include {", ".join([key for key in schema["paths"].keys()])}')

    # Index by method and responses
    try:
        logger.debug('Indexing schema by method `%s`', method.lower())
        response_indexed_schema = path_indexed_schema[method.lower()]['responses']
    except KeyError:
        raise SwaggerDocumentationError(
            f'No schema found for method {method}. Available methods include '
            f'{", ".join([method.upper() for method in path_indexed_schema.keys() if method.upper() != "PARAMETERS"])}.'
        )

    # Index by status and schema
    try:
        response_schema = response_indexed_schema[f'{status_code}']
    except KeyError:
        raise SwaggerDocumentationError(
            f'No schema found for response code `{status_code}`. Documented responses include '
            f'{", ".join([code for code in response_indexed_schema.keys()])}.'
        )

    # Not sure about this logic - this is what my static reference schema looks like, but not the drf_yasg dynamic schema
    if 'content' in response_schema and 'application/json' in response_schema['content']:
        response_schema = response_schema['content']['application/json']

    return response_schema['schema']


def format_error(error_message: str, data: Any, schema: dict, parent: str) -> SwaggerDocumentationError:
    """
    Formats and returns a standardized excetption and error message.
    """
    logger.debug('Constructing error message')

    # Unpack schema and data dicts
    schema_items = [{'key': f'{key}', 'value': f'{value}'} for key, value in schema.items()]
    schema_items += [{'key': 'parent', 'value': parent}]
    data_items = [{'key': 'data', 'value': f'{data}'}, {'key': 'type', 'value': f'{type(data)}'}]

    # Find length of items
    longest_key = max(len(f'{item["key"]}') for item_list in [schema_items, data_items] for item in item_list)
    longest_value = max(len(f'{item["value"]}') for item_list in [schema_items, data_items] for item in item_list)
    line_length = longest_value if longest_value < 91 else 91

    # Create a dotted line to make it pretty
    dotted_line = line_length * '-' + '\n'

    def format_string(left: Any, right: Any, offset: int) -> str:
        left = f'{left}'
        return left.ljust(offset) + f'{right}\n'

    # Construct data property table
    data_properties = [format_string(left=item['key'], right=item['value'], offset=longest_key + 4) for item in data_items]
    data_properties += [f'{dotted_line}\n', f'Schema\n', f'{dotted_line}']

    # Construct schema property table
    schema_properties = [format_string(left=item['key'], right=item['value'], offset=longest_key + 4) for item in schema_items]
    schema_properties += [f'{dotted_line}']

    # Construct the error message
    message = [
                  f'Item is misspecified:\n\n',
                  f'Error: {error_message}\n\n',
                  f'Response\n',
                  f'{dotted_line}',
              ] + data_properties + schema_properties  # noqa: E126

    return SwaggerDocumentationError(''.join(message))


def check_keys_match(schema_keys: KeysView, response_keys: KeysView, schema: dict, data: dict, parent: str) -> None:
    """
    Verifies that both sets have the same amount of keys.
    A length mismatch in the two sets, indicates an error in one of them.

    :param schema_keys: Schema object keys
    :param response_keys: Response dictionary keys
    :raises: SwaggerDocumentationError
    """
    #
    if len(schema_keys) != len(response_keys):
        logger.debug('The number of schema dict elements does not match the number of response dict elements')
        if len(set(response_keys)) > len(set(schema_keys)):
            missing_keys = ', '.join([f'`{key}`' for key in list(set(response_keys) - set(schema_keys))])
            raise format_error(
                f'The following properties seem to be missing from your OpenAPI/Swagger documentation: {missing_keys}.',
                data=data, schema=schema, parent=parent
            )
        else:
            missing_keys = ', '.join([f'{key}' for key in list(set(schema_keys) - set(response_keys))])
            raise format_error(
                f'The following properties seem to be missing from your response body: {missing_keys}.',
                data=data, schema=schema, parent=parent
            )
