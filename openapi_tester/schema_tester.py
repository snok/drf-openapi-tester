import logging
from typing import Any, Callable, List, Union

from inflection import camelize

from openapi_tester.configuration import settings
from openapi_tester.exceptions import DocumentationError
from openapi_tester.utils import type_placeholder_value

logger = logging.getLogger('openapi_tester')


class SchemaTester:
    def __init__(self, schema: dict, data: Any, case_tester: Callable, origin: str, **kwargs) -> None:
        """
        Iterates through an OpenAPI schema objet and an API response/request object to check that they match at every level.

        :param schema: Response/request OpenAPI schema section
        :param data: API response/request data
        :raises: openapi_tester.exceptions.DocumentationError or ImproperlyConfigured
        """
        self.case_tester = case_tester
        self.ignored_keys: List[str] = kwargs.get('ignore_case', [])
        self.ignored_keys += settings.case_passlist
        self.camel_case_parser: bool = kwargs.get('camel_case_parser', settings.camel_case_parser)
        self.origin = origin
        self._test_schema(schema=schema, data=data, reference='init')

    def _test_schema(self, schema: dict, data: dict, reference: str) -> None:
        """
        Helper method to run checks.
        """
        schema_type = schema['type']
        logger.debug(f'{reference} --> {schema_type}')
        if schema_type == 'object':
            self.test_dict(schema=schema, data=data, reference='init')
        elif schema_type == 'array':
            self.test_list(schema=schema, data=data, reference='init')
        else:
            self.test_item(schema=schema, data=data, reference='init')

    @staticmethod
    def _is_nullable(schema_item: dict) -> bool:
        """
        Checks if the item is nullable.

        OpenAPI does not have a null type, like a JSON schema,
        but in OpenAPI 3.0 they added `nullable: true` to specify that the value may be null.
        Note that null is different from an empty string "".

        This feature was back-ported to the OpenApi 2 parser as a vendored extension `x-nullable`.
        This is what drf_yasg generates.

        OpenAPI 3 ref: https://swagger.io/docs/specification/data-models/data-types/#null
        OpenApi 2 ref: https://help.apiary.io/api_101/swagger-extensions/

        :param schema_item: schema item
        :return: whether or not the item can be None
        """
        openapi_schema_3_nullable = 'nullable'
        swagger_2_nullable = 'x-nullable'
        return any(
            schema_item
            and isinstance(schema_item, dict)
            and nullable_key in schema_item
            and (
                    (isinstance(schema_item[nullable_key], bool) and schema_item)
                    or (isinstance(schema_item[nullable_key], str) and schema_item[nullable_key] == 'true')
            )
            for nullable_key in [openapi_schema_3_nullable, swagger_2_nullable]
        )

    def test_dict(self, schema: dict, data: dict, reference: str) -> None:
        """
        Verifies that an OpenAPI schema object matches a given dict.

        :param schema: OpenAPI schema
        :param data: Response/request data
        :param reference: string reference pointing to function caller
        :raises: openapi_tester.exceptions.DocumentationError
        """
        if not isinstance(data, dict):
            response_hint, request_hint = '', ''
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
            raise DocumentationError(
                message=f"Mismatched types. Expected item to be <class 'dict'> but found {type(data)}.",
                response=data,
                schema=schema,
                reference=reference,
                response_hint=response_hint or '',
                request_hint=request_hint or '',
            )

        if self.camel_case_parser:
            data = camelize(data, False)

        response_keys = data.keys()
        if 'properties' in schema:
            properties = schema['properties']
        else:
            properties = {'': schema['additionalProperties']}
        schema_keys = properties.keys()

        # Check that the response and schema has the same number of keys
        if len(schema_keys) != len(response_keys):
            logger.debug('The number of schema elements do not match the number of data elements')
            if len(set(response_keys)) > len(set(schema_keys)):
                missing_keys = ', '.join(f'`{key}`' for key in list(set(response_keys) - set(schema_keys)))

                raise DocumentationError(
                    message=f'The following properties seem to be missing from your OpenAPI/Swagger documentation: {missing_keys}.',
                    response=data,
                    schema=schema,
                    reference=reference,
                    response_hint='Add the key(s) to your OpenAPI docs, or stop returning it in your view.',
                    request_hint='Remove the excess key(s) from your request body.',
                )
            else:
                missing_keys = ', '.join(f'{key}' for key in list(set(schema_keys) - set(response_keys)))

                raise DocumentationError(
                    message=f'The following properties seem to be missing from your {self.origin} body: {missing_keys}.',
                    response=data,
                    schema=schema,
                    reference=reference,
                    response_hint='Remove the key(s) from your OpenAPI docs, or include it in your API response.',
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
                raise DocumentationError(
                    message=f'Schema key `{schema_key}` was not found in the {self.origin}.',
                    response=data,
                    schema=schema,
                    reference=reference,
                    response_hint='You need to add the missing schema key to the response, or remove it from the documented response.',
                    request_hint='You need to add the missing key to your request body.',
                )
            elif response_key not in schema_keys:
                raise DocumentationError(
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
            self._test_schema(schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}')

    def test_list(self, schema: dict, data: Union[list, dict], reference: str) -> None:
        """
        Verifies that an OpenAPI schema array matches a given list.

        :param schema: OpenAPI schema
        :param data: Response data
        :param reference: string reference pointing to function caller
        :raises: openapi_tester.exceptions.DocumentationError
        """
        if not isinstance(data, list):
            response_hint, request_hint = '', ''
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
                response_hint = (
                    'If you wish to allow null values for this schema item, your schema needs to set `x-nullable: True`.'
                    '\nFor drf-yasg implementations, set `x_nullable=True` in your Schema definition.'
                )
                request_hint = 'You passed a None value where we expected a list.'
            raise DocumentationError(
                message=f"Mismatched types. Expected item to be <class 'list'> but found {type(data)}.",
                response=data,
                schema=schema,
                reference=reference,
                response_hint=response_hint or '',
                request_hint=request_hint or '',
            )

        items = schema['items']
        if not items and data is not None:
            raise DocumentationError(
                message='Mismatched content. Response array contains data, when schema is empty.',
                response=data,
                schema=schema,
                reference=reference,
                response_hint='Document the contents of the empty dictionary to match the response object.',
                request_hint='',
            )
        for datum in data:
            items_type = items['type']
            logger.debug(f'test_list --> {items_type}')
            self._test_schema(schema=items, data=datum, reference=f'{reference}.list')

    @staticmethod
    def test_item(schema: dict, data: Any, reference: str) -> None:
        """
        Verifies that an OpenAPI schema item matches a given item.

        :param schema: OpenAPI schema
        :param data: response data item
        :param reference: string reference pointing to function caller
        :raises: openapi_tester.exceptions.DocumentationError
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
        if data is None and not SchemaTester._is_nullable(schema):
            response_hint = (
                'If you wish to allow null values for this schema item, your schema needs to set `x-nullable: True`.'
                '\nFor drf-yasg implementations, set `x_nullable=True` in your Schema definition.'
            )
            request_hint = 'You passed a None value where we expected a list.'
            raise DocumentationError(
                message=f'Mismatched types. Expected item to be {type(type_placeholder_value(schema["type"]))} but found {type(data)}.',
                response=data,
                schema=schema,
                reference=reference,
                response_hint=response_hint,
                request_hint=request_hint,
            )
        elif data is not None and schema['type'] in checks and checks[schema['type']]['check']:
            raise DocumentationError(
                message='Mismatched types.',
                response=data,
                schema=schema,
                reference=reference,
                response_hint=f'You need to change the response value type to {checks[schema["type"]]["type"]}, or change your documented type to {type(data)}.',
                request_hint=f'You need to change the value type to {checks[schema["type"]]["type"]} from {type(data)}.',
            )
