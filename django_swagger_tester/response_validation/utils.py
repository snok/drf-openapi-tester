import logging
from collections import KeysView
from typing import Any

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.openapi import index_schema
from django_swagger_tester.utils import replace_refs

logger = logging.getLogger('django_swagger_tester')


def get_response_schema(schema: dict, route: str, method: str, status_code: int) -> dict:
    """
    Indexes schema by url, HTTP method, and status code to get the section of a schema related to a specific response.

    :param schema: Full OpenAPI schema
    :param route: Schema-compatible path
    :param method: HTTP request method
    :param status_code: HTTP response code
    :return Response schema
    """
    schema = replace_refs(schema)
    # Replace all $ref sections in the schema with actual values
    no_ref_schema = replace_refs(schema)
    # Index by paths
    paths_schema = index_schema(schema=no_ref_schema, variable='paths')
    # Index by route
    route_error = f'\n\nFor debugging purposes: valid routes include {", ".join([key for key in schema.keys()])}'
    route_schema = index_schema(schema=paths_schema, variable=route, error_addon=route_error)
    # Index by method
    method_error = f'\n\nAvailable methods include {", ".join([method.upper() for method in schema.keys() if method.upper() != "PARAMETERS"])}.'
    method_schema = index_schema(schema=route_schema, variable=method.lower(), error_addon=method_error)
    # Index by responses
    responses_schema = index_schema(schema=method_schema, variable='responses')
    # Index by status code
    status_code_error = f'Documented responses include {", ".join([code for code in responses_schema.keys()])}.'
    status_code_schema = index_schema(schema=responses_schema, variable=str(status_code), error_addon=status_code_error)

    # Not sure about this logic - this is what my static reference schema looks like, but not the drf_yasg dynamic schema
    if 'content' in status_code_schema and 'application/json' in status_code_schema['content']:
        status_code_schema = status_code_schema['content']['application/json']

    return index_schema(status_code_schema, 'schema')


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
