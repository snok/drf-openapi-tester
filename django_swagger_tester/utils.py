import difflib
import json
import logging
import sys
from typing import Tuple, List

from requests import Response

from django_swagger_tester.configuration import settings
from django_swagger_tester.exceptions import SwaggerDocumentationError, CaseError

logger = logging.getLogger('django_swagger_tester')


def format_response_tester_case_error(exception: CaseError) -> str:
    """
    Returns an appropriate error message.
    """
    return (
        f'The property `{exception.key}` is not properly {exception.case}\n\n'
        f'If this is intentional, you can skip case validation by adding `ignore_case=[\'{exception.key}\']` to the '
        f'`validate_response` function call, or by adding the key to the CASE_WHITELIST in the SWAGGER_TESTER settings'
    )


def format_response_tester_error(exception: SwaggerDocumentationError, **kwargs) -> str:
    """
    Formats and returns a standardized error message for easy debugging.

    Primarily used for the django_swagger_tester.testing.response_validation function, as it's too verbose for
    middleware logging.
    """
    logger.debug('Constructing error message')

    if not hasattr(exception, 'hint'):
        exception.hint = ''

    # Construct example dict/list from schema - this is useful to display comparable items
    example_item = settings.LOADER_CLASS.create_dict_from_schema(exception.schema)

    def get_dotted_line(values: list) -> str:
        longest_value = max(len(f'{v}') for v in values)
        line_length = longest_value if longest_value < 91 else 91
        return line_length * '-' + '\n'

    # Find the max length of keys and values we're showing
    # and create a dotted line to helps us format a nice looking error message
    dotted_line = get_dotted_line(values=[exception.reference, example_item, exception.response])
    longest_key = max(len(i) for i in ['Sequence', 'Expected', 'Received'])

    example_item_string = str(example_item)
    response_string = str(exception.response)

    verbose = 'verbose' in kwargs and kwargs['verbose'] is True
    if verbose:
        tab = (longest_key + 4) * ' '

        # - Construct additional tables to be added onto the message list

        # Unpack schema and data dicts
        schema_items = [{'key': f'{key}', 'value': f'{value}'} for key, value in exception.schema.items()]
        data_items = [
            {'key': 'data', 'value': f'{exception.response}'},
            {'key': 'type', 'value': f'{type(exception.response)}'},
        ]

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
        example_item_string = f'\n{tab}' + json.dumps(example_item, indent=4, sort_keys=True).replace('\n', f'\n{tab}')
        response_string = f'\n{tab}' + json.dumps(exception.response, indent=4, sort_keys=True).replace(
            '\n', f'\n{tab}'
        )
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
        'Error:'.ljust(offset) + f'{str(exception)}\n',
        '\n',
        'Expected:'.ljust(offset) + f'{example_item_string}\n',
        'Received:'.ljust(offset) + f'{response_string}\n',
        '\n',
        'Hint:'.ljust(offset)
        + '\n'.ljust(offset + 1).join(exception.hint.split('\n'))
        + '\n',  # the join logic adds support for multi-line hints
        'Sequence:'.ljust(offset) + f'{exception.reference}\n',
        '\n' if not verbose else '',
        f'{dotted_line}',
        f'{addon}',
    ]

    return ''.join(message)


def unpack_response(response: Response) -> Tuple[dict, int]:
    """
    Unpacks HTTP response.
    """
    try:
        status_code = response.status_code
    except Exception as e:
        logger.exception('Unable to open response object')
        raise ValueError(
            f'Unable to unpack response object. Make sure you are passing response, and not response.json(). Error: {e}'
        )
    if hasattr(response, 'json'):
        return response.json(), status_code
    else:
        from django.core.exceptions import ImproperlyConfigured

        raise ImproperlyConfigured(
            'Response does not contain a JSON-formatted response and cannot be tested against a response schema.'
        )


def get_endpoint_paths() -> List[str]:
    """
    Returns a list of endpoint paths.
    """
    from rest_framework.schemas.generators import EndpointEnumerator

    return list({endpoint[0] for endpoint in EndpointEnumerator().get_api_endpoints()})


def resolve_path(endpoint_path: str) -> tuple:
    """
    Resolves a Django path.
    """
    from django.urls import Resolver404, resolve

    try:
        logger.debug('Resolving path.')
        if endpoint_path == '' or endpoint_path[0] != '/':
            logger.debug('Adding leading `/` to provided path')
            endpoint_path = '/' + endpoint_path
        try:
            resolved_route = resolve(endpoint_path)
            logger.debug('Resolved %s successfully', endpoint_path)
        except Resolver404:
            resolved_route = resolve(endpoint_path + '/')
            endpoint_path += '/'
            logger.warning('Endpoint path is missing a trailing slash: %s', endpoint_path)

        kwarg = resolved_route.kwargs
        for key, value in kwarg.items():
            # Replacing kwarg values back into the string seems to be the simplest way of bypassing complex regex
            # handling. However, its important not to freely use the .replace() function, as a {value} of `1` would
            # also cause the `1` in api/v1/ to be replaced
            var_index = endpoint_path.rfind(value)
            endpoint_path = endpoint_path[:var_index] + f'{{{key}}}' + endpoint_path[var_index + len(value) :]
        return endpoint_path, resolved_route

    except Resolver404:
        logger.error(f'URL `%s` did not resolve successfully', endpoint_path)
        paths = get_endpoint_paths()
        closest_matches = ''.join([f'\n- {i}' for i in difflib.get_close_matches(endpoint_path, paths)])
        if closest_matches:
            raise ValueError(
                f'Could not resolve path `{endpoint_path}`.\n\nDid you mean one of these?{closest_matches}\n\n'
                f'If your path contains path parameters (e.g., `/api/<version>/...`), make sure to pass a '
                f'value, and not the parameter pattern.'
            )
        raise ValueError(f'Could not resolve path `{endpoint_path}`')
