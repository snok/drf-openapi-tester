import logging
from typing import Any, List, Union

from django_swagger_tester.case_checks import case_check
from django_swagger_tester.configuration import settings
from django_swagger_tester.exceptions import SwaggerDocumentationError

logger = logging.getLogger('django_swagger_tester')


# noinspection PyMethodMayBeStatic
class SwaggerTester(object):

    def __init__(self) -> None:
        self.case_func = case_check(settings.CASE)
        self.schema = None
        self.ignore_case: List[str] = []

    def _dict(self, schema: dict, data: Union[list, dict], parent: str) -> None:
        """
        Verifies that a schema dict matches a response dict.

        :param schema: OpenAPI schema
        :param data: Response data
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
        """
        logger.debug('Verifying that response dict layer matches schema layer')

        if not isinstance(data, dict):
            raise self._error(error_message=f"Mismatched types. Expected response to be <class 'dict'> but found {type(data)}.",
                              data=data, schema=schema, parent=parent)

        schema_keys = schema['properties'].keys()
        response_keys = data.keys()

        # Verify that both dicts have the same amount of keys --> a length mismatch will always indicate an error
        if len(schema_keys) != len(response_keys):
            logger.debug('The number of schema dict elements does not match the number of response dict elements')
            if len(set(response_keys)) > len(set(schema_keys)):
                missing_keys = ', '.join([f'`{key}`' for key in list(set(response_keys) - set(schema_keys))])
                raise self._error(error_message=f'The following properties seem to be missing from your OpenAPI/Swagger documentation: '
                                                f'{missing_keys}.', data=data, schema=schema, parent=parent)
            else:
                missing_keys = ', '.join([f'{key}' for key in list(set(schema_keys) - set(response_keys))])
                raise self._error(error_message=f"The following properties seem to be missing from your response body: {missing_keys}'.",
                                  data=data, schema=schema, parent=parent)

        for schema_key, response_key in zip(schema_keys, response_keys):

            # Check the keys for case inconsistencies
            if schema_key not in self.ignore_case:
                self.case_func(schema_key)
            if response_key not in self.ignore_case:
                self.case_func(response_key)

            # Check that each element in the schema exists in the response, and vice versa
            if schema_key not in response_keys:
                raise self._error(error_message=f'Schema key `{schema_key}` was not found in the API response.',
                                  data=data, schema=schema, parent=parent)
            elif response_key not in schema_keys:
                raise self._error(error_message=f'Response key `{response_key}` not found in the OpenAPI schema.',
                                  data=data, schema=schema, parent=parent)

            # Pass nested elements for nested checks
            schema_value = schema['properties'][schema_key]
            response_value = data[schema_key]

            if schema_value['type'] == 'object':
                logger.debug('Calling _dict from _dict. Response: %s, Schema: %s', response_value, schema_value)
                self._dict(schema=schema_value, data=response_value, parent=f'{parent}.dict:key:{schema_key}')
            elif schema_value['type'] == 'array':
                logger.debug('Calling _list from _dict. Response: %s, Schema: %s', response_value, schema_value)
                self._list(schema=schema_value, data=response_value, parent=f'{parent}.dict:key:{schema_key}')
            elif schema_value['type'] in self._item_types():
                logger.debug('Calling _item from _dict. Response: %s, Schema: %s', response_value, schema_value)
                self._item(schema=schema_value, data=response_value, parent=f'{parent}.dict:key:{schema_key}')
            else:
                # This part of the code should be unreachable. However, if we do have a gap in our logic,
                # we should raise an error to highlight the error.
                raise Exception(f'Unexpected error.\n\nSchema: {schema}\nResponse: {data}\n\nThis shouldn\'t happen.')

    def _list(self, schema: dict, data: Union[list, dict], parent: str) -> None:
        """
        Verifies that the response item matches the schema documentation, when the schema layer is an array.

        :param schema: OpenAPI schema
        :param data: Response data
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
        """
        logger.debug('Verifying that response list layer matches schema layer')
        if not isinstance(data, list):
            raise self._error(error_message=f"Mismatched types. Expected response to be <class 'list'> but found {type(data)}.",
                              data=data, schema=schema, parent=parent)

        # A schema array can only hold one item, e.g., {"type": "array", "items": {"type": "object", "properties": {...}}}
        # At the same time we want to test each of the response objects, as they *should* match the schema.
        if not schema['items'] and data:
            raise self._error(error_message=f'OpenAPI schema documentation suggests an empty list, but the response contains list items.',
                              data=data, schema=schema, parent=parent)
        elif not schema['items'] and not data:
            return
        else:
            item = schema['items']

        for index in range(len(data)):

            # List item --> dict
            if item['type'] == 'object' and item['properties']:
                logger.debug('Calling _dict from _list')
                self._dict(schema=item, data=data[index], parent=f'{parent}.list')

            # List item --> empty dict  &&  response not empty
            elif (item['type'] == 'object' and not item['properties']) and data[index]:
                raise self._error(error_message=f'OpenAPI schema documentation suggests an empty dictionary, but the response contains '
                                                f'a populated dict.', data=data[index], schema=schema, parent=parent)

            # List item --> list
            elif item['type'] == 'array' and item['items']:
                logger.debug('Calling _list from _list')
                self._list(schema=item, data=data[index], parent=f'{parent}.list')

            # List item --> empty list  &&  response not empty
            elif (item['type'] == 'array' and not item['items']) and data[index]:
                # If the schema says all listed items are to be arrays, and the response has values but the schema is empty
                # ... then raise an error
                raise self._error(
                    error_message=f'OpenAPI schema documentation suggests an empty list, but the response contains list items.',
                    data=data[index], schema=schema, parent=parent)

            # List item --> item
            elif item['type'] in self._item_types():
                # If the schema says all listed items are individual items, check that the item is represented in the response
                logger.debug('Calling _item from _list')
                self._item(schema=item, data=data[index], parent=f'{parent}.list')

            else:
                # This part of the code should be unreachable. However, if we do have a gap in our logic,
                # we should raise an error to highlight the error.
                raise Exception(f'Unexpected error.\nSchema: {schema}\nResponse: {data}\n\nThis shouldn\'t happen.')

    def _item_types(self) -> List[str]:
        return ['string', 'boolean', 'integer', 'number', 'file']

    def _error(self, error_message: str, data: Any, schema: dict, parent: str) -> SwaggerDocumentationError:
        """
        Formats and returns a standardized excetption and error message.
        """
        logger.debug('Constructing error message')
        title = f'title:           {schema["title"]}\n' if 'title' in schema else ''
        example_value = f'example value:   {schema["example"]}\n' if 'example' in schema else ''
        description = f'description:     {schema["description"]}\n' if 'description' in schema else ''
        printed_item_lengths = ([len(f'{item}') for item in [data, example_value, description, type(data)]])
        dotted_line = '\n' + ((17 + max(printed_item_lengths)) * '-') + '\n'
        return SwaggerDocumentationError(f'Item is misspecified:\n\n'
                                         f'Error: {error_message}\n\n'
                                         f'Response'
                                         f'{dotted_line}'
                                         f'value:           {data}\n'
                                         f'type:            {type(data)}'
                                         f'{dotted_line}'
                                         f'\n'
                                         f'Schema'
                                         f'{dotted_line}'
                                         f'{example_value}{description}{title}'
                                         f'parent:          {parent}'
                                         f'{dotted_line}')

    def _item(self, schema: dict, data: Any, parent: str) -> None:
        """
        Verifies that a response value matches the example value in the schema.

        :param schema: OpenAPI schema
        :param data:
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
            raise self._error(error_message=f'Mismatched types.', data=data, schema=schema, parent=parent)
