import logging
from typing import Any, Callable, List, Optional

from openapi_tester.configuration import settings
from openapi_tester.exceptions import DocumentationError

logger = logging.getLogger('openapi_tester')

OPENAPI_PYTHON_MAPPING = {
    'boolean': bool.__name__,
    'string': str.__name__,
    'file': str.__name__,
    'array': list.__name__,
    'object': dict.__name__,
    'integer': int.__name__,
    'number': f'{int.__name__} or {float.__name__}',
}


class SchemaTester:
    """ SchemaTester class """

    def __init__(
        self, schema: dict, data: Any, case_tester: Optional[Callable[[str], None]], origin: str, **kwargs
    ) -> None:
        """
        Iterates through an OpenAPI schema objet and an API response/request object to check that they match at every level.

        :param schema: Response/request OpenAPI schema section
        :param data: API response/request data
        :raises: openapi_tester.exceptions.DocumentationError or ImproperlyConfigured
        """
        self.case_tester = case_tester
        self.ignored_keys: List[str] = kwargs.get('ignore_case', [])
        self.ignored_keys += settings.case_passlist
        self.origin = origin
        self.test_schema(schema=schema, data=data, reference='init')

    def _test_key_casing(self, key: str) -> None:
        if self.case_tester:
            if key not in self.ignored_keys:
                self.case_tester(key)
            else:
                logger.debug('Skipping case check for key `%s`', key)

    @staticmethod
    def _check_openapi_type(schema_type: str, value: Any) -> bool:
        if schema_type == 'boolean':
            return isinstance(value, bool)
        if schema_type == 'string' or schema_type == 'file':
            return isinstance(value, str)
        if schema_type == 'integer':
            return isinstance(value, int)
        if schema_type == 'number':
            return isinstance(value, (int, float))
        if schema_type == 'object':
            return isinstance(value, dict)
        if schema_type == 'array':
            return isinstance(value, list)

    def _test_object(self, schema: dict, data: dict, reference: str) -> None:
        """
        Verifies that an OpenAPI schema object matches a given dict.

        :param schema: OpenAPI schema
        :param data: Response/request data
        :param reference: string reference pointing to function caller
        :raises: openapi_tester.exceptions.DocumentationError
        """

        if 'properties' in schema:
            properties = schema['properties']
        else:
            properties = {'': schema['additionalProperties']}

        response_keys = data.keys()
        schema_keys = properties.keys()

        # Check that the response and schema has the same number of keys
        if len(schema_keys) != len(response_keys):
            logger.debug('The number of schema elements doesnt match the number of data elements')
            if len(response_keys) > len(schema_keys):
                missing_keys = ', '.join(f'`{key}`' for key in list(set(response_keys) - set(schema_keys)))
                response_hint = 'Add the key(s) to your OpenAPI docs, or stop returning it in your view.'
                request_hint = 'Remove the excess key(s) from your request body.'
                message = f'The following properties seem to be missing from your OpenAPI/Swagger documentation: {missing_keys}.'
            else:
                missing_keys = ', '.join(f'{key}' for key in list(set(schema_keys) - set(response_keys)))
                response_hint = 'Remove the key(s) from your OpenAPI docs, or include it in your API response.'
                request_hint = 'Remove the excess key(s) from you request body.'
                message = f'The following properties seem to be missing from your {self.origin} body: {missing_keys}.'
            raise DocumentationError(
                message=message,
                response=data,
                schema=schema,
                reference=reference,
                response_hint=response_hint,
                request_hint=request_hint,
            )

        for schema_key, response_key in zip(schema_keys, response_keys):
            self._test_key_casing(schema_key)
            self._test_key_casing(response_key)
            if schema_key not in response_keys:
                raise DocumentationError(
                    message=f'Schema key `{schema_key}` was not found in the {self.origin}.',
                    response=data,
                    schema=schema,
                    reference=reference,
                    response_hint='You need to add the missing schema key to the response, or remove it from the documented response.',
                    request_hint='You need to add the missing key to your request body.',
                )
            if response_key not in schema_keys:
                raise DocumentationError(
                    message=f'Key `{response_key}` not found in the OpenAPI schema.',
                    response=data,
                    schema=schema,
                    reference=reference,
                    response_hint='You need to add the missing schema key to your documented response, or stop returning it in your API.',
                    request_hint='You need to add the missing key to your request body.',
                )

            schema_value = properties[schema_key]
            response_value = data[schema_key]
            self.test_schema(schema=schema_value, data=response_value, reference=f'{reference}.dict:key:{schema_key}')

    def _test_array(self, schema: dict, data: list, reference: str) -> None:
        """
        Verifies that an OpenAPI schema array matches a given list.

        :param schema: OpenAPI schema
        :param data: Response data
        :param reference: string reference pointing to function caller
        :raises: openapi_tester.exceptions.DocumentationError
        """
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
            logger.debug(f'test_array --> {items_type}')
            self.test_schema(schema=items, data=datum, reference=f'{reference}.list')

    def test_schema(self, schema: dict, data: Any, reference: str) -> None:
        """
        Helper method to run checks.
        """

        schema_type = schema['type']
        logger.debug(f'{reference} --> {schema_type}')
        if data is None and self.is_nullable(schema):
            return
        if data is None or not self._check_openapi_type(schema_type, data):
            raise DocumentationError(
                message=f'Mismatched types, expected {OPENAPI_PYTHON_MAPPING[schema_type]} but received {type(data).__name__}.',
                response=data,
                schema=schema,
                reference=reference,
            )
        if schema_type == 'object':
            self._test_object(schema=schema, data=data, reference='init')
        elif schema_type == 'array':
            self._test_array(schema=schema, data=data, reference='init')

    @staticmethod
    def is_nullable(schema_item: dict) -> bool:
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
