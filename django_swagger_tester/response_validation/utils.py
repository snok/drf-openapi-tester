import json
import logging
import sys
from collections import KeysView
from typing import Any, Optional

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.input_validation.utils import serialize_schema
from django_swagger_tester.openapi import index_schema
from django_swagger_tester.utils import replace_refs

logger = logging.getLogger('django_swagger_tester')


def get_response_schema(schema: dict, route: str, method: str, status_code: Optional[int]) -> dict:
    """
    Indexes schema by url, HTTP method, and status code to get the section of a schema related to a specific response.

    :param schema: Full OpenAPI schema
    :param route: Schema-compatible path
    :param method: HTTP request method
    :param status_code: HTTP response code
    :return Response schema
    """
    # Replace all $ref sections in the schema with actual values
    no_ref_schema = replace_refs(schema)
    # Index by paths
    paths_schema = index_schema(schema=no_ref_schema, variable='paths')
    # Index by route
    route_error = f'\n\nFor debugging purposes: valid routes include {", ".join([key for key in paths_schema.keys()])}'
    route_schema = index_schema(schema=paths_schema, variable=route, error_addon=route_error)
    # Index by method
    joined_methods = ', '.join([method.upper() for method in route_schema.keys() if method.upper() != 'PARAMETERS'])
    method_error = f'\n\nAvailable methods include {joined_methods}.'
    method_schema = index_schema(schema=route_schema, variable=method.lower(), error_addon=method_error)
    # Index by responses
    responses_schema = index_schema(schema=method_schema, variable='responses')
    # Index by status code
    status_code_error = (
        f'\n\nDocumented responses include(s) {", ".join([f"`{code}`" for code in responses_schema.keys()])}. '
        f'Is the `{status_code}` response documented?'
    )
    status_code_schema = index_schema(schema=responses_schema, variable=str(status_code), error_addon=status_code_error)

    # Not sure about this logic - this is what my static schema looks like, but not the drf_yasg dynamic schema
    if 'content' in status_code_schema and 'application/json' in status_code_schema['content']:
        status_code_schema = status_code_schema['content']['application/json']

    return index_schema(status_code_schema, 'schema')


def format_error(
    error_message: str, data: Any, schema: dict, reference: str, hint: Optional[str] = None, **kwargs
) -> SwaggerDocumentationError:
    """
    Formats and returns a standardized exception and error message.
    """
    logger.debug('Constructing error message')

    if hint is None:
        hint = ''

    # Construct example dict/list from schema - this is useful to display comparable items
    example_item = serialize_schema(schema)

    def get_dotted_line(values: list) -> str:
        longest_value = max(len(f'{v}') for v in values)
        line_length = longest_value if longest_value < 91 else 91
        return line_length * '-' + '\n'

    # Find the max length of keys and values we're showing and create a dotted line to helps us format a nice looking error message
    dotted_line = get_dotted_line(values=[reference, example_item, data])
    longest_key = max(len(i) for i in ['Sequence', 'Expected', 'Received'])

    verbose = 'verbose' in kwargs and kwargs['verbose'] is True
    if verbose:
        tab = (longest_key + 4) * ' '

        # - Construct additional tables to be added onto the message list

        # Unpack schema and data dicts
        schema_items = [{'key': f'{key}', 'value': f'{value}'} for key, value in schema.items()]
        data_items = [{'key': 'data', 'value': f'{data}'}, {'key': 'type', 'value': f'{type(data)}'}]

        # Find length of items
        longest_detailed_key = max(
            len(f'{item["key"]}') for item_list in [schema_items, data_items] for item in item_list
        )

        offset = longest_detailed_key + 4
        addon = ''.join(
            [f'\nResponse details\n', f'{dotted_line}']
            + [item['key'].ljust(offset) + f'{item["value"]}\n' for item in data_items]
            + [f'{dotted_line}\n', f'Schema\n', f'{dotted_line}']
            + [item['key'].ljust(offset) + f'{item["value"]}\n' for item in schema_items]
            + [f'{dotted_line}']
        )

        # Then - For a detailed view, we change `example item` and `data` to expanded versions of themselves
        example_item: str = f'\n{tab}' + json.dumps(example_item, indent=4, sort_keys=True).replace('\n', f'\n{tab}')  # type: ignore
        data: str = f'\n{tab}' + json.dumps(data, indent=4, sort_keys=True).replace('\n', f'\n{tab}')  # type: ignore

    else:
        addon = '\n* If you need more details: set `verbose=True`'

    sys.stdout.flush()

    # Construct error message
    offset = longest_key + 4
    message = [
        f'Item is misspecified:\n\n'
        # -- Summary table --
        f'Summary',
        '\n' if not verbose else '',
        f'{dotted_line}',
        '\n',
        'Error:'.ljust(offset) + f'{error_message}\n',
        '\n',
        'Expected:'.ljust(offset) + f'{example_item}\n',
        'Received:'.ljust(offset) + f'{data}\n',
        '\n',
        'Hint:'.ljust(offset)
        + '\n'.ljust(offset + 1).join(hint.split('\n'))
        + '\n',  # the join logic adds support for multi-line hints
        'Sequence:'.ljust(offset) + f'{reference}\n',
        '\n' if not verbose else '',
        f'{dotted_line}',
        f'{addon}',
    ]

    return SwaggerDocumentationError(''.join(message))


def check_keys_match(schema_keys: KeysView, response_keys: KeysView, schema: dict, data: dict, reference: str) -> None:
    """
    Verifies that both sets have the same amount of keys.
    A length mismatch in the two sets, indicates an error in one of them.

    :param schema_keys: Schema object keys
    :param response_keys: Response dictionary keys
    :param schema: OpenAPI schema
    :param data: Response data
    :param reference: Logging reference to output for errors -
        this makes it easier to identify where in a response/schema an error is happening
    :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
    """
    if len(schema_keys) != len(response_keys):
        logger.debug('The number of schema dict elements does not match the number of response dict elements')
        if len(set(response_keys)) > len(set(schema_keys)):
            missing_keys = ', '.join([f'`{key}`' for key in list(set(response_keys) - set(schema_keys))])
            raise format_error(
                f'The following properties seem to be missing from your OpenAPI/Swagger documentation: {missing_keys}.',
                data=data,
                schema=schema,
                reference=reference,
                hint='Add the key(s) to your Swagger docs, or stop returning it in your view.',
            )
        else:
            missing_keys = ', '.join([f'{key}' for key in list(set(schema_keys) - set(response_keys))])
            raise format_error(
                f'The following properties seem to be missing from your response body: {missing_keys}.',
                data=data,
                schema=schema,
                reference=reference,
                hint='Remove the key(s) from you Swagger docs, or include it in your API response.',
            )
