import difflib
import hashlib
import json
import logging
import re
import sys
from copy import deepcopy
from typing import Any, Callable, List, Optional, Tuple

from django.core.exceptions import ImproperlyConfigured
from django.urls import ResolverMatch

from rest_framework.response import Response

from django_swagger_tester.exceptions import CaseError, SwaggerDocumentationError

logger = logging.getLogger('django_swagger_tester')


def format_response_tester_case_error(exception: CaseError) -> str:
    """
    Returns an appropriate error message.
    """
    return (
        f'The response key `{exception.key}` is not properly {exception.case}\n\n'
        f'If this is intentional, you can skip case validation by adding `ignore_case=[\'{exception.key}\']` to the '
        f'`validate_response` function call, or by adding the key to the CASE_PASSLIST in the SWAGGER_TESTER settings'
    )


def format_response_tester_error(
    exception: SwaggerDocumentationError, hint: str, addon: Optional[str] = None, **kwargs
) -> str:
    """
    Formats and returns a standardized error message for easy debugging.

    Primarily used for the django_swagger_tester.testing.response_validation function, as it's too verbose for
    middleware logging.
    """
    logger.debug('Constructing error message')

    if addon is None:
        addon = '\n* If you need more details: set `verbose=True`'

    # Construct example dict/list from schema - this is useful to display comparable items
    from django_swagger_tester.configuration import settings

    example_item = settings.loader_class.create_dict_from_schema(exception.schema)

    # Make sure we're sorting both objects to make differences easier to spot
    if isinstance(exception.response, dict):
        exception.response = dict(sorted(exception.response.items()))
    elif isinstance(exception.response, list):
        try:
            exception.response.sort()
        except TypeError:
            pass  # sorting a list of dicts doesnt work, but we don't know what the data looks like
    if isinstance(example_item, dict):
        example_item = dict(sorted(example_item.items()))
    elif isinstance(example_item, list):
        try:
            example_item.sort()
        except TypeError:
            pass  # sorting a list of dicts doesnt work, but we don't know what the data looks like

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
            ['\nResponse details\n', f'{dotted_line}']
            + [item['key'].ljust(offset) + f'{item["value"]}\n' for item in data_items]
            + [f'{dotted_line}\n', 'Schema\n', f'{dotted_line}']
            + [item['key'].ljust(offset) + f'{item["value"]}\n' for item in schema_items]
            + [f'{dotted_line}']
        )

        # Then - For a detailed view, we change `example item` and `data` to expanded versions of themselves
        example_item_string = f'\n{tab}' + json.dumps(example_item, indent=4, sort_keys=True).replace('\n', f'\n{tab}')
        response_string = f'\n{tab}' + json.dumps(exception.response, indent=4, sort_keys=True).replace(
            '\n', f'\n{tab}'
        )

    sys.stdout.flush()

    # Construct error message
    offset = longest_key + 4
    message = [
        'Item is misspecified:\n\n'
        # -- Summary table --
        'Summary\n',
        f'{dotted_line}',
        '\n',
        'Error:'.ljust(offset) + f'{str(exception)}\n',
        '\n',
        'Expected:'.ljust(offset) + f'{example_item_string}\n',
        'Received:'.ljust(offset) + f'{response_string}\n',
        '\n',
        'Hint:'.ljust(offset)
        + '\n'.ljust(offset + 1).join(hint.split('\n'))
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
        logger.exception('Unable to open response object. Error %s', e)
        raise ValueError('Response object does not contain a status code. Unable to unpack response object.')
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
        if '?' in endpoint_path:
            endpoint_path = endpoint_path.split('?')[0]
        if endpoint_path == '' or endpoint_path[0] != '/':
            logger.debug('Adding leading `/` to provided path')
            endpoint_path = '/' + endpoint_path
        if len(endpoint_path) > 2 and endpoint_path[-1] == '/':
            endpoint_path = endpoint_path[:-1]
        try:
            resolved_route = resolve(endpoint_path)
            logger.debug('Resolved %s successfully', endpoint_path)
        except Resolver404:
            resolved_route = resolve(endpoint_path + '/')
            endpoint_path += '/'
        kwarg = resolved_route.kwargs
        for key, value in kwarg.items():
            # Replacing kwarg values back into the string seems to be the simplest way of bypassing complex regex
            # handling. However, its important not to freely use the .replace() function, as a {value} of `1` would
            # also cause the `1` in api/v1/ to be replaced
            var_index = endpoint_path.rfind(str(value))
            endpoint_path = endpoint_path[:var_index] + f'{{{key}}}' + endpoint_path[var_index + len(str(value)) :]
        return endpoint_path, resolved_route

    except Resolver404:
        logger.warning('URL `%s` did not resolve successfully', endpoint_path)
        paths = get_endpoint_paths()
        closest_matches = ''.join(f'\n- {i}' for i in difflib.get_close_matches(endpoint_path, paths))
        if closest_matches:
            raise ValueError(
                f'Could not resolve path `{endpoint_path}`.\n\nDid you mean one of these?{closest_matches}\n\n'
                f'If your path contains path parameters (e.g., `/api/<version>/...`), make sure to pass a '
                f'value, and not the parameter pattern.'
            )
        raise ValueError(f'Could not resolve path `{endpoint_path}`')


class Route:
    def __init__(self, deparameterized_path: str, resolved_path: ResolverMatch) -> None:
        self.deparameterized_path = deparameterized_path
        self.parameterized_path = deparameterized_path
        self.resolved_path = resolved_path

        # Used to create a next() type logic
        self.counter = 0
        self.parameters = self.get_parameters(self.deparameterized_path)

    def get_parameters(self, path: str) -> List[str]:
        """
        Returns a count of parameters in a string.
        """
        pattern = re.compile(r'({[\w]+})')  # noqa: FS003
        return list(re.findall(pattern, path))

    def get_path(self) -> str:
        """
        Given an original deparameterized path looking like this:

            /api/{version}/{parameter1}/{parameter2}

        This should return the path, with one parameter substituted every time it's called, until there are no more
        parameters to insert. Like this:

        > route.get_path()
        >> /api/{version}/{parameter1}/{parameter2}

        > route.get_path()
        >> /api/v1/{parameter1}/{parameter2}

        > route.get_path()
        >> /api/v1/cars/{parameter2}

        > route.get_path()
        >> /api/v1/cars/correct

        > route.get_path()
        >> IndexError('No more parameters to insert')
        """
        if self.counter == 0:
            self.counter += 1
            return self.replace_i18n_parameter(self.parameterized_path)
        if self.counter > len(self.parameters):
            raise IndexError('No more parameters to insert')

        path = self.parameterized_path
        parameter = self.parameters[self.counter - 1]
        parameter_name = parameter.replace('{', '').replace('}', '')
        starting_index = path.find(parameter)
        path = f'{path[:starting_index]}{self.resolved_path.kwargs[parameter_name]}{path[starting_index + len(parameter):]}'
        self.parameterized_path = path
        self.counter += 1

        return self.replace_i18n_parameter(path)

    def reset(self) -> None:
        """
        Resets parameterized path and counter.
        """
        self.parameterized_path = self.deparameterized_path
        self.counter = 0

    def route_matches(self, route: str) -> bool:
        """
        Checks whether a route matches any version of get_path.
        """
        if len(self.parameters) == 0:
            return self.deparameterized_path == route

        for _ in range(len(self.parameters) + 1):
            x = self.get_path()
            if x == route:
                self.reset()
                return True
        self.reset()
        return False

    @staticmethod
    def replace_i18n_parameter(route: str):
        """
        If PARAMETERIZED_I18N_NAME is set in the package settings,
        this function will replace a route with a parameter value.

        In short, this route

            /en/api/v1/items

        Would become

            /{language}/api/v1/items

        If PARAMETERIZED_I18N_NAME == 'language'. If it was 'lang', the route
        would become

            /{lang}/api/v1/items
        """
        from django.utils import translation

        from django_swagger_tester.configuration import settings

        if settings.parameterized_i18n_name:
            parameter = f'{{{settings.parameterized_i18n_name}}}'
            language = translation.get_language()
            route = route.replace(f'/{language}/', f'/{parameter}/')

        return route


def type_placeholder_value(_type: str) -> Any:
    """
    Returns a placeholder example value for schema items without one.
    """
    if _type == 'boolean':
        return True
    elif _type == 'integer':
        return 1
    elif _type == 'number':
        return 1.0
    elif _type in ['string', 'file']:
        return 'string'
    else:
        raise TypeError(f'Cannot return placeholder value for {_type}')


def camelize(data: dict) -> dict:
    """
    Adapted djangorestframework.utils.camelize function for converting a snake_cased dict to camelCase.
    """
    from djangorestframework_camel_case.util import camelize_re, underscore_to_camel

    new_dict = {}
    for key, value in data.items():
        if isinstance(key, str) and '_' in key:
            new_key = re.sub(camelize_re, underscore_to_camel, key)
        else:
            new_key = key
        new_dict[new_key] = value
    return new_dict


def copy_response(response: Response) -> Response:
    """
    Loads response data as JSON and returns a copied response object.
    """
    # By parsing the response data JSON we bypass problems like uuid's not having been converted to
    # strings yet, which otherwise would create problems when comparing response data types to the
    # documented schema types in the schema tester
    content = response.content.decode(response.charset)
    response_data = json.loads(content) if response.status_code != 204 and content else {}
    copied_response = deepcopy(response)
    copied_response.data = response_data
    return copied_response


def get_logger(level: str, logger_name: str) -> Callable:
    """
    Return logger.

    :param level: log level
    :param logger_name: logger name
    :return: logger
    """
    error = (
        f'`{level}` is not a valid log level. Please change the `LOG_LEVEL` setting in your `SWAGGER_TESTER` '
        f'settings to one of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `EXCEPTION`, or `CRITICAL`.'
    )
    if not isinstance(level, str):
        raise ImproperlyConfigured(error)
    if not isinstance(logger_name, str):
        raise ImproperlyConfigured('Logger name must be a string')
    else:
        level = level.upper()
    if level == 'DEBUG':
        return logging.getLogger(logger_name).debug
    elif level == 'INFO':
        return logging.getLogger(logger_name).info
    elif level == 'WARNING':
        return logging.getLogger(logger_name).warning
    elif level == 'ERROR':
        return logging.getLogger(logger_name).error
    elif level == 'EXCEPTION':
        return logging.getLogger(logger_name).exception
    elif level == 'CRITICAL':
        return logging.getLogger(logger_name).critical
    else:
        raise ImproperlyConfigured(error)


def hash_response(response: dict) -> str:
    """
    Function replaces all response values with type-specific placeholder values, and returns a hash value.

    The idea is that we don't have to validate the same response twice, unless response types change.
    """
    types = {str: 0, int: 1, bool: 2, float: 3, type(None): 4}

    def iterate_list(_list: list) -> list:
        new_list = []
        for item in _list:
            if isinstance(item, dict):
                new_list.append(iterate_dict(item))
            elif isinstance(item, list):
                new_list.append(iterate_list(item))  # type: ignore
            elif isinstance(item, tuple(types)):
                new_list.append(types[type(item)])  # type: ignore
        return new_list

    def iterate_dict(d: dict) -> dict:
        new_dict = {}
        for k, v in d.items():
            if isinstance(v, dict):
                new_dict[k] = iterate_dict(v)
            elif isinstance(v, list):
                new_dict[k] = iterate_list(v)  # type: ignore
            elif isinstance(v, tuple(types)):
                new_dict[k] = types[type(v)]  # type: ignore
        return new_dict

    if isinstance(response, dict):
        result = iterate_dict(response)
    elif isinstance(response, list):
        result = iterate_list(response)
    elif isinstance(response, tuple(types)):
        result = types[type(response)]

    return str(int(hashlib.sha1(bytes(str(result), 'utf-8')).hexdigest(), 16))


def hash_schema(o: dict) -> str:
    """
    Makes a hash out of anything that contains only list, dict and hashable types including string and numeric types.

    Stolen from https://stackoverflow.com/questions/5884066/hashing-a-dictionary
    """

    def freeze(o: Any) -> Any:
        if isinstance(o, dict):
            return frozenset({k: freeze(v) for k, v in o.items()}.items())

        if isinstance(o, list):
            return tuple(freeze(v) for v in o)

        return o

    return str(hash(freeze(o)))
