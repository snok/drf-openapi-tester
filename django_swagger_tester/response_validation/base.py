import logging
from django.core.exceptions import ImproperlyConfigured
from typing import Any, Union

from django_swagger_tester.openapi import is_nullable, list_types, read_items, read_properties, read_type
from django_swagger_tester.response_validation.utils import check_keys_match, format_error

logger = logging.getLogger('django_swagger_tester')


# noinspection PyMethodMayBeStatic
class ResponseTester:
    def __init__(self, response_schema: dict, response_data: Any, **kwargs) -> None:
        """
        Iterates through both a response schema and an actual API response to check that they match.

        :param response_schema: Response OpenAPI schema section
        :param response_data: API response data
        raises: django_swagger_tester.exceptions.SwaggerDocumentationError or ImproperlyConfigured
        """
        if '$ref' in str(response_schema):
            # `$ref`s should be replaced inplace before the schema is passed to this class
            raise ImproperlyConfigured(
                'Received invalid schema. You must replace $ref sections before passing a schema for validation.'
            )

        if read_type(response_schema) == 'object':
            logger.debug('init --> dict')
            self.test_dict(schema=response_schema, data=response_data, reference='init', **kwargs)
        elif read_type(response_schema) == 'array':
            logger.debug('init --> list')
            self.test_list(schema=response_schema, data=response_data, reference='init', **kwargs)
        # this should always be third, as list_types also contains `array` and `object`
        elif read_type(response_schema) in list_types():
            logger.debug('init --> item')
            self.test_item(schema=response_schema, data=response_data, reference='init', **kwargs)

    def test_dict(self, schema: dict, data: Union[list, dict], reference: str, **kwargs) -> None:
        """
        Verifies that a schema dict matches a response dict.

        :param schema: OpenAPI schema
        :param data: Response data
        :param reference: string reference pointing to function caller
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
        """
        if not isinstance(data, dict):
            hint = ''
            if isinstance(data, list):
                hint = 'The expected item should be a dict, or your schema should be a list.'
            elif data is None:
                if 'x-nullable' in schema and schema['x-nullable']:
                    # NoneTypes are OK if the schema says the field is nullable
                    return
                hint = (
                    'If you wish to allow null values for this schema item, your schema needs to set `x-nullable: True`.'
                    '\nFor drf-yasg implementations, set `x_nullable=True` in your Schema definition.'
                )
            raise format_error(
                error_message=f"Mismatched types. Expected response to be <class 'dict'> but found {type(data)}.",
                data=data,
                schema=schema,
                reference=reference,
                hint=hint,
                **kwargs,
            )

        properties = read_properties(schema)
        schema_keys = properties.keys()
        response_keys = data.keys()
        check_keys_match(schema_keys, response_keys, schema, data, reference)

        for schema_key, response_key in zip(schema_keys, response_keys):

            # Check that each element in the schema exists in the response, and vice versa
            if schema_key not in response_keys:
                raise format_error(
                    error_message=f'Schema key `{schema_key}` was not found in the API response.',
                    data=data,
                    schema=schema,
                    reference=reference,
                    hint='You need to add the missing schema key to the response, or remove it from the documented response.',
                    **kwargs,
                )
            elif response_key not in schema_keys:
                raise format_error(
                    error_message=f'Response key `{response_key}` not found in the OpenAPI schema.',
                    data=data,
                    schema=schema,
                    reference=reference,
                    hint='You need to add the missing schema key to your documented response, or stop returning it in your API.',
                    **kwargs,
                )

            # Pass nested elements to the appropriate function
            schema_value = properties[schema_key]
            response_value = data[schema_key]

            if read_type(schema_value) == 'object':
                logger.debug('test_dict --> test_dict. Response: %s, Schema: %s', response_value, schema_value)
                self.test_dict(
                    schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}', **kwargs
                )
            elif read_type(schema_value) == 'array':
                logger.debug('test_dict --> test_list. Response: %s, Schema: %s', response_value, schema_value)
                self.test_list(
                    schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}', **kwargs
                )
            elif read_type(schema_value) in list_types():  # This needs to come after array and object test_checks
                logger.debug('test_dict --> test_item. Response: %s, Schema: %s', response_value, schema_value)
                self.test_item(
                    schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}', **kwargs
                )

    def test_list(self, schema: dict, data: Union[list, dict], reference: str, **kwargs) -> None:
        """
        Verifies that a schema array matches a response list.

        :param schema: OpenAPI schema
        :param data: Response data
        :param reference: string reference pointing to function caller
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
        """
        if not isinstance(data, list):
            hint = ''
            if isinstance(data, dict):
                hint = 'You might need to wrap your response item in a list, or remove the excess list layer from your documented response.'
            elif data is None:
                if 'x-nullable' in schema and schema['x-nullable']:
                    # NoneTypes are OK if the schema says the field is nullable
                    return
            hint = (
                'If you wish to allow null values for this schema item, your schema needs to set `x-nullable: True`.'
                '\nFor drf-yasg implementations, set `x_nullable=True` in your Schema definition.'
            )
            raise format_error(
                error_message=f"Mismatched types. Expected response to be <class 'list'> but found {type(data)}.",
                data=data,
                schema=schema,
                reference=reference,
                hint=hint,
                **kwargs,
            )

        item = read_items(schema)
        for index in range(len(data)):

            if read_type(item) == 'object':
                logger.debug('test_list --> test_dict')
                self.test_dict(schema=item, data=data[index], reference=f'{reference}.list', **kwargs)

            elif read_type(item) == 'array':
                logger.debug('test_list --> test_dict')
                self.test_list(schema=item, data=data[index], reference=f'{reference}.list', **kwargs)

            elif read_type(item) in list_types():
                logger.debug('test_list --> test_item')
                self.test_item(schema=item, data=data[index], reference=f'{reference}.list', **kwargs)

    def test_item(self, schema: dict, data: Any, reference: str, **kwargs) -> None:
        """
        Verifies that a response value matches the example value in the schema.

        :param schema: OpenAPI schema
        :param data: response data item
        :param reference: string reference pointing to function caller
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
        """
        checks = {
            'boolean': {
                'check': not isinstance(data, bool)
                and not (isinstance(data, str) and (data.lower() == 'true' or data.lower() == 'false')),
                'type': "<class 'bool'>",
            },
            'string': {'check': not isinstance(data, str) and data is not None, 'type': "<class 'str'>"},
            'integer': {'check': not isinstance(data, int) and data is not None, 'type': "<class 'int'>"},
            'number': {'check': not isinstance(data, float) and data is not None, 'type': "<class 'float'>"},
            'file': {'check': not isinstance(data, str) and data is not None, 'type': "<class 'str'>"},
        }
        if data is None and is_nullable(schema):
            return
        elif checks[schema['type']]['check']:
            raise format_error(
                error_message=f'Mismatched types.',
                data=data,
                schema=schema,
                reference=reference,
                hint=f'You need to change the response value type to {checks[schema["type"]]["type"]}, '
                f'or change your documented type to {type(data)}.',
                **kwargs,
            )
