import logging
from typing import Any, Union, Callable, List

from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.validation.utils.openapi import (
    is_nullable,
    list_types,
    read_items,
    read_properties,
    read_type,
)

logger = logging.getLogger('django_swagger_tester')


class SchemaTester:
    def __init__(self, schema: dict, data: Any, case_tester: Callable, **kwargs) -> None:
        """
        Iterates through a response schema and an actual API response to check that they match at every level.

        :param schema: Response OpenAPI schema section
        :param data: API response data
        raises: django_swagger_tester.exceptions.SwaggerDocumentationError or ImproperlyConfigured
        """
        self.case_tester = case_tester
        self.ignored_keys: List[str] = []
        if 'ignore_case' in kwargs:
            self.ignored_keys = kwargs['ignore_case']

        if '$ref' in str(schema):
            # `$ref`s should be replaced with values before the schema is passed here
            raise ImproperlyConfigured(
                'Received invalid schema. You must replace $ref sections before passing a schema for validation.'
            )

        if read_type(schema) == 'object':
            logger.debug('init --> dict')
            self.test_dict(
                schema=schema, data=data, reference='init',
            )
        elif read_type(schema) == 'array':
            logger.debug('init --> list')
            self.test_list(
                schema=schema, data=data, reference='init',
            )
        # this should always be third, as list_types() also contains `array` and `object`
        elif read_type(schema) in list_types():
            logger.debug('init --> item')
            self.test_item(
                schema=schema, data=data, reference='init',
            )

    def test_dict(self, schema: dict, data: Union[list, dict], reference: str,) -> None:
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
                    'If you wish to allow null values for this schema item, your schema needs to '
                    'set `x-nullable: True`.\nFor drf-yasg implementations, set `x_nullable=True` '
                    'in your Schema definition.'
                )
            raise SwaggerDocumentationError(
                message=f"Mismatched types. Expected response to be <class 'dict'> but found {type(data)}.",
                response=data,
                schema=schema,
                reference=reference,
                hint=hint,
            )

        properties = read_properties(schema)
        schema_keys = properties.keys()
        response_keys = data.keys()

        # Check that the response and schema has the same number of keys
        if len(schema_keys) != len(response_keys):
            logger.debug('The number of schema dict elements does not match the number of response dict elements')
            if len(set(response_keys)) > len(set(schema_keys)):
                missing_keys = ', '.join([f'`{key}`' for key in list(set(response_keys) - set(schema_keys))])
                raise SwaggerDocumentationError(
                    message=f'The following properties seem to be missing from your OpenAPI/Swagger documentation: {missing_keys}.',
                    response=data,
                    schema=schema,
                    reference=reference,
                    hint='Add the key(s) to your Swagger docs, or stop returning it in your view.',
                )
            else:
                missing_keys = ', '.join([f'{key}' for key in list(set(schema_keys) - set(response_keys))])
                raise SwaggerDocumentationError(
                    message=f'The following properties seem to be missing from your response body: {missing_keys}.',
                    response=data,
                    schema=schema,
                    reference=reference,
                    hint='Remove the key(s) from you Swagger docs, or include it in your API response.',
                )

        for schema_key, response_key in zip(schema_keys, response_keys):

            # Check the case of each key
            self.case_tester(schema_key, 'schema')
            self.case_tester(response_key, 'response')

            # Check that each element in the schema exists in the response, and vice versa
            if schema_key not in response_keys:
                raise SwaggerDocumentationError(
                    message=f'Schema key `{schema_key}` was not found in the API response.',
                    response=data,
                    schema=schema,
                    reference=reference,
                    hint='You need to add the missing schema key to the response, '
                    'or remove it from the documented response.',
                )
            elif response_key not in schema_keys:
                raise SwaggerDocumentationError(
                    message=f'Response key `{response_key}` not found in the OpenAPI schema.',
                    response=data,
                    schema=schema,
                    reference=reference,
                    hint='You need to add the missing schema key to your documented response, '
                    'or stop returning it in your API.',
                )

            # Pass nested elements to the appropriate function
            schema_value = properties[schema_key]
            response_value = data[schema_key]

            if read_type(schema_value) == 'object':
                logger.debug('test_dict --> test_dict. Response: %s, Schema: %s', response_value, schema_value)
                self.test_dict(
                    schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}',
                )
            elif read_type(schema_value) == 'array':
                logger.debug('test_dict --> test_list. Response: %s, Schema: %s', response_value, schema_value)
                self.test_list(
                    schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}',
                )
            elif read_type(schema_value) in list_types():  # This needs to come after array and object test_checks
                logger.debug('test_dict --> test_item. Response: %s, Schema: %s', response_value, schema_value)
                self.test_item(
                    schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}',
                )

    def test_list(self, schema: dict, data: Union[list, dict], reference: str,) -> None:
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
            raise SwaggerDocumentationError(
                message=f"Mismatched types. Expected response to be <class 'list'> but found {type(data)}.",
                response=data,
                schema=schema,
                reference=reference,
                hint=hint,
            )

        item = read_items(schema)
        if not item and data:
            raise SwaggerDocumentationError(
                message=f'Mismatched content. Response array contains data, when schema is empty.',
                response=data,
                schema=schema,
                reference=reference,
                hint='Document the contents of the empty dictionary to match the response object.',
            )
        for datum in data:
            if read_type(item) == 'object':
                logger.debug('test_list --> test_dict')
                self.test_dict(
                    schema=item, data=datum, reference=f'{reference}.list',
                )

            elif read_type(item) == 'array':
                logger.debug('test_list --> test_dict')
                self.test_list(
                    schema=item, data=datum, reference=f'{reference}.list',
                )

            elif read_type(item) in list_types():
                logger.debug('test_list --> test_item')
                self.test_item(
                    schema=item, data=datum, reference=f'{reference}.list',
                )

    @staticmethod
    def test_item(schema: dict, data: Any, reference: str,) -> None:
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
            raise SwaggerDocumentationError(
                message=f'Mismatched types.',
                response=data,
                schema=schema,
                reference=reference,
                hint=f'You need to change the response value type to {checks[schema["type"]]["type"]}, '
                f'or change your documented type to {type(data)}.',
            )
