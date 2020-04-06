import logging
from typing import Any, Union

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.utils import item_types, replace_refs

logger = logging.getLogger('django_swagger_tester')


class ResponseTester:

    def __init__(self, response_schema: dict, response_data: Any) -> None:
        assert '$ref' not in str(response_schema)  # OpenAPI schema should have all $ref sections replaced before being passed to the class
        if response_schema['type'] == 'object':
            self.dict(schema=response_schema, data=response_data, parent='init')
        elif response_schema['type'] == 'array':
            self.list(schema=response_schema, data=response_data, parent='init')
        elif response_schema['type'] in item_types():
            self.item(schema=response_schema, data=response_data, parent='init')
        else:
            raise Exception(f'Unexpected error.\nSchema: {response_schema}\nResponse: {response_data}\n\nThis shouldn\'t happen.')

    def dict(self, schema: dict, data: Union[list, dict], parent: str) -> None:
        """
        Verifies that a schema dict matches a response dict.

        :param schema: OpenAPI schema
        :param data: Response data
        :param parent: string reference pointing to function caller
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
        """
        logger.debug('Verifying that response dict layer matches schema layer')

        if not isinstance(data, dict):
            raise self.error(error_message=f"Mismatched types. Expected response to be <class 'dict'> but found {type(data)}.",
                             data=data, schema=schema, parent=parent)

        schema_keys = schema['properties'].keys()
        response_keys = data.keys()

        # Verify that both dicts have the same amount of keys --> a length mismatch will always indicate an error
        if len(schema_keys) != len(response_keys):
            logger.debug('The number of schema dict elements does not match the number of response dict elements')
            if len(set(response_keys)) > len(set(schema_keys)):
                missing_keys = ', '.join([f'`{key}`' for key in list(set(response_keys) - set(schema_keys))])
                raise self.error(error_message=f'The following properties seem to be missing from your OpenAPI/Swagger documentation: '
                                               f'{missing_keys}.', data=data, schema=schema, parent=parent)
            else:
                missing_keys = ', '.join([f'{key}' for key in list(set(schema_keys) - set(response_keys))])
                raise self.error(error_message=f'The following properties seem to be missing from your response body: {missing_keys}.',
                                 data=data, schema=schema, parent=parent)

        for schema_key, response_key in zip(schema_keys, response_keys):

            # Check that each element in the schema exists in the response, and vice versa
            if schema_key not in response_keys:
                raise self.error(error_message=f'Schema key `{schema_key}` was not found in the API response.',
                                 data=data, schema=schema, parent=parent)
            elif response_key not in schema_keys:
                raise self.error(error_message=f'Response key `{response_key}` not found in the OpenAPI schema.',
                                 data=data, schema=schema, parent=parent)

            # Pass nested elements for nested checks
            schema_value = schema['properties'][schema_key]
            response_value = data[schema_key]

            if schema_value['type'] == 'object':
                logger.debug('Calling _dict from _dict. Response: %s, Schema: %s', response_value, schema_value)
                self.dict(schema=schema_value, data=response_value, parent=f'{parent}.dict:key:{schema_key}')
            elif schema_value['type'] == 'array':
                logger.debug('Calling _list from _dict. Response: %s, Schema: %s', response_value, schema_value)
                self.list(schema=schema_value, data=response_value, parent=f'{parent}.dict:key:{schema_key}')
            elif schema_value['type'] in item_types():
                logger.debug('Calling _item from _dict. Response: %s, Schema: %s', response_value, schema_value)
                self.item(schema=schema_value, data=response_value, parent=f'{parent}.dict:key:{schema_key}')
            else:
                # This part of the code should be unreachable. However, if we do have a gap in our logic,
                # we should raise an error to highlight the error.
                raise Exception(f'Unexpected error.\n\nSchema: {schema}\nResponse: {data}\n\nThis shouldn\'t happen.')

    def list(self, schema: dict, data: Union[list, dict], parent: str) -> None:
        """
        Verifies that the response item matches the schema documentation, when the schema layer is an array.

        :param schema: OpenAPI schema
        :param data: Response data
        :param parent: string reference pointing to function caller
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
        """
        logger.debug('Verifying that response list layer matches schema layer')
        if not isinstance(data, list):
            raise self.error(error_message=f"Mismatched types. Expected response to be <class 'list'> but found {type(data)}.",
                             data=data, schema=schema, parent=parent)

        # A schema array can only hold one item, e.g., {"type": "array", "items": {"type": "object", "properties": {...}}}
        # At the same time we want to test each of the response objects, as they *should* match the schema.
        if not schema['items'] and data:
            raise self.error(error_message=f'OpenAPI schema documentation suggests an empty list, but the response contains list items.',
                             data=data, schema=schema, parent=parent)
        elif not schema['items'] and not data:
            return
        else:
            item = schema['items']

        for index in range(len(data)):

            # List item --> dict
            if item['type'] == 'object' and item['properties']:
                logger.debug('Calling _dict from _list')
                self.dict(schema=item, data=data[index], parent=f'{parent}.list')

            # List item --> empty dict  &&  response not empty
            elif (item['type'] == 'object' and not item['properties']) and data[index]:
                raise self.error(error_message=f'OpenAPI schema documentation suggests an empty dictionary, but the response contains '
                                               f'a populated dict.', data=data[index], schema=schema, parent=parent)

            # List item --> list
            elif item['type'] == 'array' and item['items']:
                logger.debug('Calling _list from _list')
                self.list(schema=item, data=data[index], parent=f'{parent}.list')

            # List item --> empty list  &&  response not empty
            elif (item['type'] == 'array' and not item['items']) and data[index]:
                # If the schema says all listed items are to be arrays, and the response has values but the schema is empty
                # ... then raise an error
                raise self.error(
                    error_message=f'OpenAPI schema documentation suggests an empty list, but the response contains list items.',
                    data=data[index], schema=schema, parent=parent)

            # List item --> item
            elif item['type'] in item_types():
                # If the schema says all listed items are individual items, check that the item is represented in the response
                logger.debug('Calling _item from _list')
                self.item(schema=item, data=data[index], parent=f'{parent}.list')

            else:
                # This part of the code should be unreachable. However, if we do have a gap in our logic,
                # we should raise an error to highlight the error.
                raise Exception(f'Unexpected error.\nSchema: {schema}\nResponse: {data}\n\nThis shouldn\'t happen.')

    def item(self, schema: dict, data: Any, parent: str) -> None:
        """
        Verifies that a response value matches the example value in the schema.

        :param schema: OpenAPI schema
        :param data: response data item
        :param parent: string reference pointing to function caller
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
        """
        checks = {
            'boolean': {
                'check': not isinstance(data, bool) and not (isinstance(data, str) and (data.lower() == 'true' or data.lower() == 'false')),
                'type': "<class 'bool'>"},
            'string': {'check': not isinstance(data, str) and data is not None, 'type': "<class 'str'>"},
            'integer': {'check': not isinstance(data, int) and data is not None, 'type': "<class 'int'>"},
            'number': {'check': not isinstance(data, float) and data is not None, 'type': "<class 'float'>"},
            'file': {'check': not isinstance(data, str) and data is not None, 'type': "<class 'str'>"},
        }
        if checks[schema['type']]['check']:
            raise self.error(error_message=f'Mismatched types.', data=data, schema=schema, parent=parent)

    @staticmethod
    def error(error_message: str, data: Any, schema: dict, parent: str) -> SwaggerDocumentationError:
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
            f'\n\nFor debugging purposes: valid urls include {", ".join([key for key in schema.keys()])}')

    # Index by method and responses
    try:
        logger.debug('Indexing schema by method `%s`', method.lower())
        response_indexed_schema = path_indexed_schema[method.lower()]['responses']
    except KeyError:
        raise SwaggerDocumentationError(
            f'No schema found for method {method}. Available methods include '
            f'{", ".join([method.upper() for method in schema.keys() if method.upper() != "PARAMETERS"])}.'
        )

    # Index by status and schema
    try:
        response_schema = response_indexed_schema[f'{status_code}']['schema']
    except KeyError:
        raise SwaggerDocumentationError(
            f'No schema found for response code `{status_code}`. Documented responses include '
            f'{", ".join([code for code in schema.keys()])}.'
        )

    return response_schema
