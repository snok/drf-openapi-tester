import logging

from response_tester.exceptions import UndocumentedSchemaSectionError

logger = logging.getLogger('response_tester')


def is_nullable(schema_item: dict) -> bool:
    """
    Checks if the item is nullable.

    OpenAPI does not have a null type, like a JSON schema,
    but in OpenAPI 3.0 they added `nullable: true` to specify that the value may be null.
    Note that null is different from an empty string "".

    This feature was back-ported to the Swagger 2 parser as a vendored extension `x-nullable`.
    This is what drf_yasg generates.

    OpenAPI 3 ref: https://swagger.io/docs/specification/data-models/data-types/#null
    Swagger 2 ref: https://help.apiary.io/api_101/swagger-extensions/

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


def index_schema(schema: dict, variable: str, error_addon: str = '') -> dict:
    """
    Indexes schema by string variable.

    :param schema: Schema to index
    :param variable: Variable to index by
    :param error_addon: Additional error info to be included in the printed error message
    :return: Indexed schema
    :raises: IndexError
    """
    try:
        logger.debug('Indexing schema by `%s`', variable)
        return schema[variable]
    except KeyError:
        raise UndocumentedSchemaSectionError(
            f'Failed indexing schema.\n\n'
            f'Error: Unsuccessfully tried to index the OpenAPI schema by `{variable}`. {error_addon}'
        )
