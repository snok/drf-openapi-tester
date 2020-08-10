import logging
from collections import KeysView
from typing import Any, Union, Optional, Tuple

from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.schema_validation.error import format_error
from django_swagger_tester.schema_validation.openapi import (
    is_nullable,
    list_types,
    read_items,
    read_properties,
    read_type,
)

logger = logging.getLogger('django_swagger_tester')


def check_keys_match(
    schema_keys: KeysView, response_keys: KeysView, schema: dict, data: dict, reference: str
) -> Tuple[Optional[str], Optional[str]]:
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
            return format_error(
                f'The following properties seem to be missing from your OpenAPI/Swagger documentation: {missing_keys}.',
                data=data,
                schema=schema,
                reference=reference,
                hint='Add the key(s) to your Swagger docs, or stop returning it in your view.',
            )
        else:
            missing_keys = ', '.join([f'{key}' for key in list(set(schema_keys) - set(response_keys))])
            return format_error(
                f'The following properties seem to be missing from your response body: {missing_keys}.',
                data=data,
                schema=schema,
                reference=reference,
                hint='Remove the key(s) from you Swagger docs, or include it in your API response.',
            )
    return None, None


class SchemaTester:
    def __init__(self, response_schema: dict, response_data: Any, **kwargs) -> None:
        """
        Iterates through both a response schema and an actual API response to check that they match.

        :param response_schema: Response OpenAPI schema section
        :param response_data: API response data
        raises: django_swagger_tester.exceptions.SwaggerDocumentationError or ImproperlyConfigured
        """
        self.error = None
        self.formatted_error = None

        if '$ref' in str(response_schema):
            # `$ref`s should be replaced inplace before the schema is passed to this class
            raise ImproperlyConfigured(
                'Received invalid schema. You must replace $ref sections before passing a schema for validation.'
            )

        if read_type(response_schema) == 'object':
            logger.debug('init --> dict')
            self.formatted_error, self.error = self.test_dict(
                schema=response_schema, data=response_data, reference='init', **kwargs
            )
        elif read_type(response_schema) == 'array':
            logger.debug('init --> list')
            self.formatted_error, self.error = self.test_list(
                schema=response_schema, data=response_data, reference='init', **kwargs
            )
        # this should always be third, as list_types also contains `array` and `object`
        elif read_type(response_schema) in list_types():
            logger.debug('init --> item')
            self.formatted_error, self.error = self.test_item(
                schema=response_schema, data=response_data, reference='init', **kwargs
            )

    def test_dict(
        self, schema: dict, data: Union[list, dict], reference: str, **kwargs
    ) -> Tuple[Optional[str], Optional[str]]:
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
                    return None, None
                hint = (
                    'If you wish to allow null values for this schema item, your schema needs to '
                    'set `x-nullable: True`.\nFor drf-yasg implementations, set `x_nullable=True` '
                    'in your Schema definition.'
                )
            return format_error(
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
        formatted_error, error = check_keys_match(schema_keys, response_keys, schema, data, reference)
        if error:
            return formatted_error, error

        for schema_key, response_key in zip(schema_keys, response_keys):

            # Check that each element in the schema exists in the response, and vice versa
            if schema_key not in response_keys:
                return format_error(
                    error_message=f'Schema key `{schema_key}` was not found in the API response.',
                    data=data,
                    schema=schema,
                    reference=reference,
                    hint='You need to add the missing schema key to the response, '
                    'or remove it from the documented response.',
                    **kwargs,
                )
            elif response_key not in schema_keys:
                return format_error(
                    error_message=f'Response key `{response_key}` not found in the OpenAPI schema.',
                    data=data,
                    schema=schema,
                    reference=reference,
                    hint='You need to add the missing schema key to your documented response, '
                    'or stop returning it in your API.',
                    **kwargs,
                )

            # Pass nested elements to the appropriate function
            schema_value = properties[schema_key]
            response_value = data[schema_key]

            if read_type(schema_value) == 'object':
                logger.debug('test_dict --> test_dict. Response: %s, Schema: %s', response_value, schema_value)
                return self.test_dict(
                    schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}', **kwargs
                )
            elif read_type(schema_value) == 'array':
                logger.debug('test_dict --> test_list. Response: %s, Schema: %s', response_value, schema_value)
                return self.test_list(
                    schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}', **kwargs
                )
            elif read_type(schema_value) in list_types():  # This needs to come after array and object test_checks
                logger.debug('test_dict --> test_item. Response: %s, Schema: %s', response_value, schema_value)
                return self.test_item(
                    schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}', **kwargs
                )
        return None, None

    def test_list(
        self, schema: dict, data: Union[list, dict], reference: str, **kwargs
    ) -> Tuple[Optional[str], Optional[str]]:
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
                hint = (
                    'You might need to wrap your response item in a list, or remove the excess list '
                    'layer from your documented response.\n'
                )
            elif data is None:
                if 'x-nullable' in schema and schema['x-nullable']:
                    # NoneTypes are OK if the schema says the field is nullable
                    return
            hint += (
                'If you wish to allow null values for this schema item, your schema needs to set `x-nullable: True`.'
                '\nFor drf-yasg implementations, set `x_nullable=True` in your Schema definition.'
            )
            return format_error(
                error_message=f"Mismatched types. Expected response to be <class 'list'> but found {type(data)}.",
                data=data,
                schema=schema,
                reference=reference,
                hint=hint,
                **kwargs,
            )

        item = read_items(schema)
        if not item and data:
            return format_error(
                error_message=f'Mismatched content. Response array contains data, when schema is empty.',
                data=data,
                schema=schema,
                reference=reference,
                hint='Document the contents of the empty dictionary to match the response object.',
                **kwargs,
            )
        for datum in data:
            if read_type(item) == 'object':
                logger.debug('test_list --> test_dict')
                return self.test_dict(schema=item, data=datum, reference=f'{reference}.list', **kwargs,)

            elif read_type(item) == 'array':
                logger.debug('test_list --> test_dict')
                return self.test_list(schema=item, data=datum, reference=f'{reference}.list', **kwargs,)

            elif read_type(item) in list_types():
                logger.debug('test_list --> test_item')
                return self.test_item(schema=item, data=datum, reference=f'{reference}.list', **kwargs,)
        return None, None

    @staticmethod
    def test_item(schema: dict, data: Any, reference: str, **kwargs) -> Tuple[Optional[str], Optional[str]]:
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
                and not (isinstance(data, str) and data.lower() in ['true', 'false']),
                'type': "<class 'bool'>",
            },
            'string': {'check': not isinstance(data, str) and data is not None, 'type': "<class 'str'>"},
            'integer': {'check': not isinstance(data, int) and data is not None, 'type': "<class 'int'>"},
            'number': {'check': not isinstance(data, float) and data is not None, 'type': "<class 'float'>"},
            'file': {'check': not (isinstance(data, str) or data is None), 'type': "<class 'str'>"},
        }

        if data is None and is_nullable(schema):
            pass
        elif checks[schema['type']]['check']:
            return format_error(
                error_message=f'Mismatched types.',
                data=data,
                schema=schema,
                reference=reference,
                hint=f'You need to change the response value type to {checks[schema["type"]]["type"]}, '
                f'or change your documented type to {type(data)}.',
                **kwargs,
            )
        return None, None
