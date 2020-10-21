import logging
from typing import Any, Callable, List, Union

from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.openapi import is_nullable, list_types, read_items, read_properties, read_type
from django_swagger_tester.utils import camelize, type_placeholder_value

logger = logging.getLogger('django_swagger_tester')


class SchemaTester:
    def __init__(self, schema: dict, data: Any, case_tester: Callable, origin: str, **kwargs) -> None:
        """
        Iterates through an OpenAPI schema objet and an API response/request object to check that they match at every level.

        :param schema: Response/request OpenAPI schema section
        :param data: API response/request data
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError or ImproperlyConfigured
        """
        from django_swagger_tester.configuration import settings

        self.case_tester = case_tester
        self.ignored_keys: List[str] = kwargs['ignore_case'] if 'ignore_case' in kwargs else []
        self.ignored_keys += settings.case_passlist
        self.camel_case_parser: bool = (
            kwargs['camel_case_parser'] if 'camel_case_parser' in kwargs else settings.camel_case_parser
        )
        self.origin = origin

        if '$ref' in str(schema):
            # `$ref`s should be replaced in the schema before passed to the class
            raise ImproperlyConfigured(
                'Received invalid schema. You must replace $ref sections before passing a schema for validation.'
            )

        if read_type(schema) == 'object':
            logger.debug('init --> dict')
            self.test_dict(schema=schema, data=data, reference='init')
        elif read_type(schema) == 'array':
            logger.debug('init --> list')
            self.test_list(schema=schema, data=data, reference='init')
        elif read_type(schema) in list_types(cut=['array', 'object']):
            logger.debug('init --> item')
            self.test_item(schema=schema, data=data, reference='init')

    def test_dict(self, schema: dict, data: dict, reference: str) -> None:
        """
        Verifies that an OpenAPI schema object matches a given dict.

        :param schema: OpenAPI schema
        :param data: Response/request data
        :param reference: string reference pointing to function caller
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
        """
        if not isinstance(data, dict):
            request_hint, response_hint = '', ''
            if isinstance(data, list):
                response_hint = 'The expected item should be a dict, or your schema should be a list.'
                request_hint = 'You passed a list where the expected item should be a dict.'
            elif data is None:
                if 'x-nullable' in schema and schema['x-nullable']:
                    # NoneTypes are OK if the schema says the field is nullable
                    return
                response_hint = (
                    'If you wish to allow null values for this schema item, your schema needs to '
                    'set `x-nullable: True`.\nFor drf-yasg implementations, set `x_nullable=True` '
                    'in your Schema definition.'
                )
                request_hint = 'You passed a None value where we expected a dict.'
            raise SwaggerDocumentationError(
                message=f"Mismatched types. Expected item to be <class 'dict'> but found {type(data)}.",
                response=data,
                schema=schema,
                reference=reference,
                response_hint=response_hint,
                request_hint=request_hint,
            )

        if self.camel_case_parser:
            data = camelize(data)

        response_keys = data.keys()
        properties = read_properties(schema)
        schema_keys = properties.keys()

        # Check that the response and schema has the same number of keys
        if len(schema_keys) != len(response_keys):
            logger.debug('The number of schema elements do not match the number of data elements')
            if len(set(response_keys)) > len(set(schema_keys)):
                missing_keys = ', '.join([f'`{key}`' for key in list(set(response_keys) - set(schema_keys))])
                raise SwaggerDocumentationError(
                    message=f'The following properties seem to be missing from your OpenAPI/Swagger documentation: {missing_keys}.',
                    response=data,
                    schema=schema,
                    reference=reference,
                    response_hint='Add the key(s) to your Swagger docs, or stop returning it in your view.',
                    request_hint='Remove the excess key(s) from your request body.',
                )
            else:
                missing_keys = ', '.join([f'{key}' for key in list(set(schema_keys) - set(response_keys))])
                raise SwaggerDocumentationError(
                    message=f'The following properties seem to be missing from your {self.origin} body: {missing_keys}.',
                    response=data,
                    schema=schema,
                    reference=reference,
                    response_hint='Remove the key(s) from you Swagger docs, or include it in your API response.',
                    request_hint='Remove the excess key(s) from you request body.',
                )

        for schema_key, response_key in zip(schema_keys, response_keys):

            # Case checks
            if schema_key not in self.ignored_keys:
                self.case_tester(schema_key, 'schema')
            else:
                logger.debug('Skipping case check for key `%s`', schema_key)
            if response_key not in self.ignored_keys:
                self.case_tester(response_key, 'response')
            else:
                logger.debug('Skipping case check for key `%s`', response_key)

            # Check that each element in the schema exists in the response, and vice versa
            if schema_key not in response_keys:
                raise SwaggerDocumentationError(
                    message=f'Schema key `{schema_key}` was not found in the {self.origin}.',
                    response=data,
                    schema=schema,
                    reference=reference,
                    response_hint='You need to add the missing schema key to the response, or remove it from the documented response.',
                    request_hint='You need to add the missing key to your request body.',
                )
            elif response_key not in schema_keys:
                raise SwaggerDocumentationError(
                    message=f'Key `{response_key}` not found in the OpenAPI schema.',
                    response=data,
                    schema=schema,
                    reference=reference,
                    response_hint='You need to add the missing schema key to your documented response, or stop returning it in your API.',
                    request_hint='You need to add the missing key to your request body.',
                )

            # Pass nested elements to the appropriate function
            schema_value = properties[schema_key]
            response_value = data[schema_key]

            if read_type(schema_value) == 'object':
                logger.debug('test_dict --> test_dict')
                self.test_dict(schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}')
            elif read_type(schema_value) == 'array':
                logger.debug('test_dict --> test_list')
                self.test_list(schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}')
            elif read_type(schema_value) in list_types(cut=['array', 'object']):
                logger.debug('test_dict --> test_item')
                self.test_item(schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}')

    def test_list(self, schema: dict, data: Union[list, dict], reference: str) -> None:
        """
        Verifies that an OpenAPI schema array matches a given list.

        :param schema: OpenAPI schema
        :param data: Response data
        :param reference: string reference pointing to function caller
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
        """
        if not isinstance(data, list):
            request_hint, response_hint = '', ''
            if isinstance(data, dict):
                response_hint = (
                    'You might need to wrap your response item in a list, or remove the excess list '
                    'layer from your documented response.\n'
                )
                request_hint = 'Received a dict where we expected the item to be a list'
            elif data is None:
                if 'x-nullable' in schema and schema['x-nullable']:
                    # NoneTypes are OK if the schema says the field is nullable
                    return
                response_hint += (
                    'If you wish to allow null values for this schema item, your schema needs to set `x-nullable: True`.'
                    '\nFor drf-yasg implementations, set `x_nullable=True` in your Schema definition.'
                )
                request_hint = 'You passed a None value where we expected a list.'
            raise SwaggerDocumentationError(
                message=f"Mismatched types. Expected item to be <class 'list'> but found {type(data)}.",
                response=data,
                schema=schema,
                reference=reference,
                response_hint=response_hint,
                request_hint=request_hint,
            )

        item = read_items(schema)
        if not item and data:
            raise SwaggerDocumentationError(
                message='Mismatched content. Response array contains data, when schema is empty.',
                response=data,
                schema=schema,
                reference=reference,
                response_hint='Document the contents of the empty dictionary to match the response object.',
                request_hint='',
            )
        for datum in data:
            if read_type(item) == 'object':
                logger.debug('test_list --> test_dict')
                self.test_dict(schema=item, data=datum, reference=f'{reference}.list')

            elif read_type(item) == 'array':
                logger.debug('test_list --> test_dict')
                self.test_list(schema=item, data=datum, reference=f'{reference}.list')

            elif read_type(item) in list_types(cut=['array', 'object']):
                logger.debug('test_list --> test_item')
                self.test_item(schema=item, data=datum, reference=f'{reference}.list')

    @staticmethod
    def test_item(schema: dict, data: Any, reference: str) -> None:
        """
        Verifies that an OpenAPI schema item matches a given item.

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
            'string': {'check': not isinstance(data, str), 'type': "<class 'str'>"},
            'integer': {'check': not isinstance(data, int), 'type': "<class 'int'>"},
            'number': {'check': not isinstance(data, float), 'type': "<class 'float'>"},
            'file': {'check': not (isinstance(data, str)), 'type': "<class 'str'>"},
        }
        response_hint = ''
        if data is None and is_nullable(schema):
            pass  # this is fine
        elif data is None and not is_nullable(schema):
            response_hint += (
                'If you wish to allow null values for this schema item, your schema needs to set `x-nullable: True`.'
                '\nFor drf-yasg implementations, set `x_nullable=True` in your Schema definition.'
            )
            request_hint = 'You passed a None value where we expected a list.'
            raise SwaggerDocumentationError(
                message=f'Mismatched types. Expected item to be {type(type_placeholder_value(read_type(schema)))} but found {type(data)}.',
                response=data,
                schema=schema,
                reference=reference,
                response_hint=response_hint,
                request_hint=request_hint,
            )
        elif checks[schema['type']]['check']:
            raise SwaggerDocumentationError(
                message='Mismatched types.',
                response=data,
                schema=schema,
                reference=reference,
                response_hint=f'You need to change the response value type to {checks[schema["type"]]["type"]}, or change your documented type to {type(data)}.',
                request_hint=f'You need to change the value type to {checks[schema["type"]]["type"]} from {type(data)}.',
            )
