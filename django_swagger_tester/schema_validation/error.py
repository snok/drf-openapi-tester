import json
import logging
import sys
from typing import Any, Optional

from django_swagger_tester.configuration import settings
from django_swagger_tester.exceptions import SwaggerDocumentationError

logger = logging.getLogger('django_swagger_tester')


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
    example_item = settings.LOADER_CLASS.create_dict_from_schema(schema)

    def get_dotted_line(values: list) -> str:
        longest_value = max(len(f'{v}') for v in values)
        line_length = longest_value if longest_value < 91 else 91
        return line_length * '-' + '\n'

    # Find the max length of keys and values we're showing
    # and create a dotted line to helps us format a nice looking error message
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
        example_item: str = f'\n{tab}' + json.dumps(example_item, indent=4, sort_keys=True).replace(
            '\n', f'\n{tab}'
        )  # type: ignore
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
