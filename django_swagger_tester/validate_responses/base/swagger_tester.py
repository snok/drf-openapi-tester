import logging
from typing import Any, Union

from django_swagger_tester.case_checks import case_check
from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.validate_responses.base.configuration import load_settings

logger = logging.getLogger('django_swagger_tester')


class SwaggerTester(object):

    def __init__(self) -> None:
        self.case_func = None
        self.schema = None
        self._validation()

    def _validation(self) -> None:
        """
        Loads Django settings.

        This method should hold base-setting validation.
        Currently the `CASE` setting is the only required setting, but this might be extended in the future.
        """
        settings = load_settings()
        self.case_func = case_check(settings['CASE'])

    def _dict(self, schema: dict, data: Union[list, dict]) -> None:
        """
        Verifies that a schema dict matches a response dict.

        :param schema: OpenAPI schema
        :param data: Response data
        :return: None
        """
        logger.debug('Verifying that response dict layer matches schema layer')

        if not isinstance(data, dict):
            raise SwaggerDocumentationError(
                f"The response is {type(data)} where it should be <class 'dict'>.\n\nResponse: {data}\n\nSchema: {schema}")

        schema_keys = schema['properties'].keys()
        response_keys = data.keys()

        # Verify that both dicts have the same amount of keys --> a length mismatch will always indicate an error
        if len(schema_keys) != len(response_keys):
            logger.debug('The number of schema dict elements does not match the number of response dict elements')
            if len(set(response_keys)) > len(set(schema_keys)):
                missing_keys = ', '.join([f'`{key}`' for key in list(set(response_keys) - set(schema_keys))])
                raise SwaggerDocumentationError(
                    f'The following properties seem to be missing from your OpenAPI/Swagger documentation: {missing_keys}')
            else:
                missing_keys = ', '.join([f'{key}' for key in list(set(schema_keys) - set(response_keys))])
                raise SwaggerDocumentationError(
                    f'The following properties seem to be missing from your response body' f': {missing_keys}')

        for schema_key, response_key in zip(schema_keys, response_keys):

            # Check the keys for case inconsistencies
            self.case_func(schema_key)
            self.case_func(response_key)

            # Check that each element in the schema exists in the response, and vice versa
            if schema_key not in response_keys:
                raise SwaggerDocumentationError(
                    f'Schema key `{schema_key}` was not found in the API response. '
                    f'Response keys include: {", ".join([i for i in data.keys()])}'
                )
            elif response_key not in schema_keys:
                raise SwaggerDocumentationError(f'Response key `{response_key}` is missing from your API documentation')

            # Pass nested elements for nested checks
            schema_value = schema['properties'][schema_key]
            response_value = data[schema_key]

            if schema_value['type'] == 'object':
                logger.debug('Calling _dict from _dict. Response: %s, Schema: %s', response_value, schema_value)
                self._dict(schema=schema_value, data=response_value)
            elif schema_value['type'] == 'array':
                logger.debug('Calling _list from _dict. Response: %s, Schema: %s', response_value, schema_value)
                self._list(schema=schema_value, data=response_value)
            elif schema_value['type'] in ['string', 'boolean', 'integer', 'number']:
                logger.debug('Calling _item from _dict. Response: %s, Schema: %s', response_value, schema_value)
                self._item(schema=schema_value, data=response_value)
            else:
                # This part of the code should be unreachable. However, if we do have a gap in our logic,
                # we should raise an error to highlight the error.
                raise Exception(f'Unexpected error.\nSchema: {schema}\nResponse: {data}\n\nThis shouldn\'t happen.')

    def _list(self, schema: dict, data: Union[list, dict]) -> None:
        """
        Verifies that the response item matches the schema documentation, when the schema layer is an array.

        :param schema: OpenAPI schema
        :param data: Response data
        :return: None.
        """
        logger.debug('Verifying that response list layer matches schema layer')
        if not isinstance(data, list):
            raise SwaggerDocumentationError(f"The response is {type(data)} when it should be <class 'list'>."
                                            f'\n\nResponse: {data}\n\nSchema: {schema}')

        # A schema array can only hold one item, e.g., {"type": "array", "items": {"type": "object", "properties": {...}}}
        # At the same time we want to test each of the response objects, as they *should* match the schema.
        if not schema['items'] and data:
            raise SwaggerDocumentationError(f'Response list contains values `{data}` '
                                            f'where schema suggests there should be an empty list.')
        elif not schema['items'] and not data:
            return
        else:
            item = schema['items']

        for index in range(len(data)):

            # List item --> dict
            if item['type'] == 'object' and item['properties']:
                self._dict(schema=item, data=data[index])

            # List item --> empty dict  &&  response not empty
            elif (item['type'] == 'object' and not item['properties']) and data[index]:
                raise SwaggerDocumentationError(f'Response dict contains value `{data[index]}` '
                                                f'where schema suggests there should be an empty dict.')

            # List item --> list
            elif item['type'] == 'array' and item['items']:
                self._list(schema=item, data=data[index])

            # List item --> empty list  &&  response not empty
            elif (item['type'] == 'array' and not item['items']) and data[index]:
                # If the schema says all listed items are to be arrays, and the response has values but the schema is empty
                # ... then raise an error
                raise SwaggerDocumentationError(f'Response list contains value `{data[index]}` '
                                                f'where schema suggests there should be an empty list.')

            # List item --> item
            elif item['type'] in ['string', 'boolean', 'integer', 'number']:
                # If the schema says all listed items are individual items, check that the item is represented in the response
                self._item(schema=item, data=data)

            else:
                # This part of the code should be unreachable. However, if we do have a gap in our logic,
                # we should raise an error to highlight the error.
                raise Exception(f'Unexpected error.\nSchema: {schema}\nResponse: {data}\n\nThis shouldn\'t happen.')

    @staticmethod
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
                raise SwaggerDocumentationError(
                    f"The example value `{schema['example']}` does not match the specified data type <type 'bool'>.")
        elif schema['type'] == 'string':
            if not isinstance(data, str) and data is not None:
                raise SwaggerDocumentationError(
                    f"The example value `{schema['example']}` does not match the specified data type <type 'str>'.")
        elif schema['type'] in ['integer', 'number']:
            if not isinstance(data, int) and data is not None:
                raise SwaggerDocumentationError(
                    f"The example value `{schema['example']}` does not match the specified data type <class 'int'>.")
        else:
            # This part of the code should be unreachable. However, if we do have a gap in our logic,
            # we should raise an error to highlight the error.
            raise Exception(f'Unexpected error.\nSchema: {schema}\nResponse: {data}\n\nThis shouldn\'t happen.')
