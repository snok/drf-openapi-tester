"""
This file should contain a collection of schema-parsing utility functions.

While this package should never become an OpenAPI schema parser,
it is useful for us to apply the rules of the schema specifiction
in case we're ever dealt with an incorrect schema.

Instead of raising unhandled errors, it is useful for us to raise appropriate exceptions.
"""
from typing import List

from django_swagger_tester.exceptions import OpenAPISchemaError


def read_items(array: dict) -> dict:
    """
    Accesses the `items` attribute of an array.

    Rule: `items – must be present if type is array. The item schema must be an OpenAPI schema and not a standard JSON`
    https://swagger.io/docs/specification/data-models/keywords/

    :param array: schema array
    :return: array items
    :raises: OpenAPISchemaError
    """
    if 'items' not in array:
        raise OpenAPISchemaError(f'Array is missing an `items` attribute.\n\nArray schema: {array}')
    return array['items']


def list_types() -> List[str]:
    """
    Returns supported item types.
    """
    return ['string', 'boolean', 'integer', 'number', 'file', 'object', 'array']


def read_type(item: dict) -> str:
    """
    Accesses the `items` attribute of a schema item.

    Rule: `type – the value must be a single type and not an array of types.
            null is not supported as a type, use the`nullable: true keyword instead.`

    :param item: schema item
    :return: schema item type
    :raises: OpenAPISchemaError
    """
    if 'type' not in item or not item['type'] or not isinstance(item['type'], str):
        raise OpenAPISchemaError(f'Schema item has an invalid `type` attribute. The type should be a single string.\n\nSchema item: {item}')
    if not item['type'] in list_types():
        raise OpenAPISchemaError(
            f'Schema item has an invalid `type` attribute. The type {item["type"]} is not supported.\n\nSchema item: {item}')
    return item['type']


def read_additional_properties(schema_object: dict) -> dict:
    """
    Accesses the `additionalProperties` attribute of a schema object.

    :param schema_object: schema object (dict)
    :return: schema object additional properties
    :raises: OpenAPISchemaError
    """
    if 'additionalProperties' not in schema_object:
        raise OpenAPISchemaError(f'Object is missing a `additionalProperties` attribute.\n\nObject schema: {schema_object}')
    return schema_object['additionalProperties']


def read_properties(schema_object: dict) -> dict:
    """
    Accesses the `properties` attribute of a schema object.

    :param schema_object: schema object (dict)
    :return: schema object properties
    :raises: OpenAPISchemaError
    """
    if 'properties' not in schema_object:
        if 'additionalProperties' in schema_object:
            return read_additional_properties(schema_object)
        raise OpenAPISchemaError(f'Object is missing a `properties` attribute.\n\nObject schema: {schema_object}')
    return schema_object['properties']


def is_nullable(schema_item: dict) -> bool:
    """
    Checks if the item is nullable.

    OpenAPI does not have a null type, like a JSON schema,
    but in OpenAPI 3.0 they added `nullable: true` to specify that the value may be null.
    Note that null is different from an empty string "".

    This feature was backported to the Swagger 2 parser as a vendored extension `x-nullable`. This is what drf_yasg generates.

    OpenAPI 3 ref: https://swagger.io/docs/specification/data-models/data-types/#null
    Swagger 2 ref: https://help.apiary.io/api_101/swagger-extensions/

    :param schema_item: schema item
    :return: whether or not the item can be None
    """
    openapi_schema_3_nullable = 'nullable' in schema_item and schema_item['nullable']
    swagger_2_nullable = 'x-nullable' in schema_item and schema_item['x-nullable']
    return swagger_2_nullable or openapi_schema_3_nullable
